from __future__ import annotations
import time
import logging
from threading import Thread, Event
from collections import deque
from typing import Callable, Optional
from .account import Account
from .types import Chat, ChatMessage

logger = logging.getLogger("vhd.listener")


class NewMessageEvent:
    def __init__(self, chat: Chat, message: ChatMessage):
        self.chat = chat
        self.message = message


class EventListener:
    """
    Слушатель новых сообщений через polling.
    Опрашивает /chats каждые N секунд и сравнивает last_message.
    """

    def __init__(self, account: Account, poll_interval: float = 5.0):
        self.account = account
        self.poll_interval = poll_interval
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._known_last_msg: dict[str, str] = {}  # chat_id -> last_message_id
        self._processed_msgs: deque = deque(maxlen=500)

        # Колбэки
        self._on_new_message: list[Callable[[NewMessageEvent], None]] = []

    def on_new_message(self, func: Callable[[NewMessageEvent], None]):
        """Декоратор/метод для подписки на новые сообщения."""
        self._on_new_message.append(func)
        return func

    def start(self):
        """Запустить слушатель в фоновом потоке."""
        self._stop_event.clear()
        self._thread = Thread(target=self._poll_loop, daemon=True, name="VitalSharkListener")
        self._thread.start()
        logger.info("Слушатель событий запущен")

    def stop(self):
        """Остановить слушатель."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("Слушатель событий остановлен")

    def _poll_loop(self):
        # Инициализация — запомнить текущие last_message
        try:
            chats = self.account.get_chats()
            for chat in chats:
                if chat.last_message:
                    self._known_last_msg[chat.id] = chat.last_message.id
        except Exception as e:
            logger.error(f"Ошибка инициализации слушателя: {e}")

        while not self._stop_event.is_set():
            try:
                self._check_new_messages()
            except Exception as e:
                logger.error(f"Ошибка в цикле опроса: {e}")
            self._stop_event.wait(self.poll_interval)

    def _check_new_messages(self):
        chats = self.account.get_chats()
        for chat in chats:
            if not chat.last_message:
                continue
            last_id = chat.last_message.id
            known_id = self._known_last_msg.get(chat.id)

            if known_id is None:
                self._known_last_msg[chat.id] = last_id
                continue

            if last_id == known_id:
                continue

            # Есть новые сообщения — получаем их
            self._known_last_msg[chat.id] = last_id
            try:
                messages = self.account.get_chat_messages(chat.id)
                for msg in messages:
                    if msg.id in self._processed_msgs:
                        continue
                    if msg.id == known_id:
                        break
                    self._processed_msgs.appendleft(msg.id)
                    # Не реагируем на свои сообщения
                    if self.account.profile and msg.sender_id == self.account.profile.id:
                        continue
                    event = NewMessageEvent(chat=chat, message=msg)
                    for cb in self._on_new_message:
                        try:
                            cb(event)
                        except Exception as e:
                            logger.error(f"Ошибка в обработчике new_message: {e}")
            except Exception as e:
                logger.error(f"Ошибка получения сообщений чата {chat.id}: {e}")
