from __future__ import annotations
import asyncio
import logging
import sys
from colorama import Fore, init as colorama_init

from settings import load_config, save_config
from vhd_api.account import Account, PLATFORMS
from vhd_api.listener import EventListener
from vhd_api.exceptions import UnauthorizedError
from tgbot.handlers import set_account
from aiogram import Bot

colorama_init()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger("vhd")

for _noisy in ("aiogram", "aiohttp", "asyncio"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)


def setup_first_run() -> dict:
    print(f"\n{Fore.CYAN}{'='*50}\n  VHD-Universal — первый запуск\n{'='*50}{Fore.RESET}\n")
    cfg = load_config()

    # Выбор площадки
    if not cfg["vhd-universal-account"].get("platform"):
        print(f"{Fore.YELLOW}Выберите площадку:{Fore.RESET}")
        print("  1. VitalShark.ru")
        print("  2. Holdik.ru")
        print("  3. Donater.shop")
        _platform_map = {"1": "vitalshark", "2": "holdik", "3": "donater"}
        while True:
            choice = input(f"\n{Fore.GREEN}Введите номер (1/2/3): {Fore.RESET}").strip()
            if choice in _platform_map:
                cfg["vhd-universal-account"]["platform"] = _platform_map[choice]
                print(f"{Fore.CYAN}✅ Выбрана площадка: {['VitalShark.ru','Holdik.ru','Donater.shop'][int(choice)-1]}{Fore.RESET}\n")
                break
            print(f"{Fore.RED}Введите 1, 2 или 3{Fore.RESET}")

    platform = cfg["vhd-universal-account"]["platform"]

    if not cfg["vhd-universal-account"]["access_token"]:
        _domain_map = {"vitalshark": "vitalshark.ru", "holdik": "holdik.ru", "donater": "donater.shop"}
        domain = _domain_map[platform]
        print(f"{Fore.YELLOW}Как получить access_token:{Fore.RESET}")
        print(f"  1. Войдите на {domain}")
        print("  2. Откройте DevTools (F12) → Application → Cookies")
        print(f"  3. Скопируйте значение {Fore.CYAN}access_token{Fore.RESET}\n")
        token = input(f"{Fore.GREEN}Введите access_token: {Fore.RESET}").strip()
        if not token:
            print(f"{Fore.RED}Токен не может быть пустым!{Fore.RESET}")
            sys.exit(1)
        print(f"\n{Fore.YELLOW}Проверяю токен...{Fore.RESET}")
        try:
            acc = Account(access_token=token, platform=platform)
            profile = acc.get_me()
            print(f"{Fore.GREEN}✅ Авторизован как: {profile.name}{Fore.RESET}")
            cfg["vhd-universal-account"]["access_token"] = token
        except UnauthorizedError:
            print(f"{Fore.RED}❌ Неверный токен!{Fore.RESET}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка: {e}{Fore.RESET}")
            sys.exit(1)

    if not cfg["telegram"]["token"]:
        print(f"\n{Fore.YELLOW}Введите токен Telegram бота{Fore.RESET} (получить у @BotFather)\n")
        tg_token = input(f"{Fore.GREEN}Telegram bot token: {Fore.RESET}").strip()
        if not tg_token:
            print(f"{Fore.RED}Токен не может быть пустым!{Fore.RESET}")
            sys.exit(1)
        cfg["telegram"]["token"] = tg_token

    if not cfg["telegram"]["admin_id"]:
        print(f"\n{Fore.YELLOW}Введите ваш Telegram ID{Fore.RESET} (узнать у @userinfobot)\n")
        try:
            cfg["telegram"]["admin_id"] = int(input(f"{Fore.GREEN}Ваш Telegram ID: {Fore.RESET}").strip())
        except ValueError:
            print(f"{Fore.RED}ID должен быть числом!{Fore.RESET}")
            sys.exit(1)

    save_config(cfg)
    print(f"\n{Fore.GREEN}✅ Настройка завершена!{Fore.RESET}\n")
    return cfg


def start_listener(account: Account, notify_queue: asyncio.Queue) -> EventListener:
    listener = EventListener(account, poll_interval=5.0)

    @listener.on_new_message
    def on_message(event):
        try:
            cfg = load_config()
            chat = event.chat
            msg = event.message

            if not msg.text:
                return

            # Авто-ответчик
            ar_cfg = cfg["auto_response"]
            if ar_cfg["enabled"] and chat.type == "private":
                text_lower = msg.text.lower()
                for trigger, reply in ar_cfg["commands"].items():
                    if trigger in text_lower:
                        try:
                            account.send_message(chat.id, reply)
                            logger.info(f"Авто-ответ на «{trigger}»")
                        except Exception as e:
                            logger.error(f"Ошибка авто-ответа: {e}")
                        break

            # Уведомление в Telegram
            tg_log = cfg["tg_logging"]
            if tg_log["enabled"] and tg_log["events"]["new_message"] and chat.type == "private":
                admin_id = cfg["telegram"]["admin_id"]
                if admin_id:
                    from tgbot.templates import new_message_notify
                    text = new_message_notify(chat, msg)
                    notify_queue.put_nowait((admin_id, text))
        except UnauthorizedError:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"  ❌ Токен истёк во время работы!")
            print(f"{'='*60}{Fore.RESET}")
            print(f"\nТокен VitalShark истёк или неверный.")
            print(f"Обновите поле {Fore.YELLOW}'access_token'{Fore.RESET} в файле:")
            print(f"{Fore.CYAN}bot_settings/config.json{Fore.RESET}")
            print(f"Затем перезапустите бота.\n")
            sys.exit(1)

    listener.start()
    return listener


async def _notification_worker(bot, queue: asyncio.Queue):
    """Отправляет уведомления из очереди в Telegram."""
    while True:
        admin_id, text = await queue.get()
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
        queue.task_done()


async def _set_bot_description(bot: Bot, platform: str):
    """Обновляет описание бота в зависимости от выбранной площадки."""
    platform_info = PLATFORMS.get(platform, {})
    name = platform_info.get("name", "VitalShark")
    domain = platform_info.get("domain", "vitalshark.ru")
    desc = f"""🌐 VHD-Universal

👤 Профиль и баланс
📦 Управление товарами
💬 Чаты и сообщения
🤖 Авто-ответчик
📋 Заказы
🔔 Уведомления
🌐 Прокси
🏪 Площадка: {name}
🌐 RU/EN
📸 Фото лотов

🛠 github.com/Human001User/VHD-Universal
👨‍💻 @DeleteWindows
💰 @vhd_donate
🔄 @vhd_updates
💬 @vhd_chat"""
    try:
        await bot.set_my_description(desc)
    except Exception:
        pass


async def main():
    cfg = setup_first_run()

    proxy = cfg["vhd-universal-account"].get("proxy") or None
    if not cfg["vhd-universal-account"].get("proxy_enabled", False):
        proxy = None
    timeout = cfg["vhd-universal-account"].get("requests_timeout", 30)
    platform = cfg["vhd-universal-account"].get("platform", "vitalshark")
    account = Account(access_token=cfg["vhd-universal-account"]["access_token"], platform=platform, proxy=proxy, timeout=timeout)

    try:
        profile = account.get_me()
        logger.info(f"Аккаунт: {profile.name} | Баланс: {profile.balance.available} ₽")
    except UnauthorizedError:
        print(f"\n{Fore.RED}{'='*60}")
        print(f"  ❌ Ошибка авторизации!")
        print(f"{'='*60}{Fore.RESET}")
        print(f"\nТокен истёк или неверный.")
        print(f"Откройте файл: {Fore.CYAN}bot_settings/config.json{Fore.RESET}")
        print(f"Обновите поле {Fore.YELLOW}'access_token'{Fore.RESET} и перезапустите бота.\n")
        sys.exit(1)

    set_account(account)

    from aiogram import Bot, Dispatcher
    from aiogram.client.session.aiohttp import AiohttpSession
    from tgbot import router

    tg_proxy = cfg["telegram"].get("proxy") or None
    session = AiohttpSession(proxy=f"http://{tg_proxy}") if tg_proxy else None
    bot = Bot(token=cfg["telegram"]["token"], session=session)
    dp = Dispatcher()
    dp.include_router(router)

    notify_queue: asyncio.Queue = asyncio.Queue()
    listener = start_listener(account, notify_queue)

    print(f"{Fore.CYAN}🤖 VHD-Universal запущен! Напишите /start в Telegram.{Fore.RESET}\n")
    logger.info("Telegram бот запущен")

    # Обновляем описание бота
    await _set_bot_description(bot, platform)

    worker = asyncio.create_task(_notification_worker(bot, notify_queue))
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        worker.cancel()
        listener.stop()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
