# VHD-Universal

Telegram-бот для управления аккаунтами на торговых площадках игровых товаров.

### Поддерживаемые платформы

| Платформа | Ссылка |
|-----------|--------|
| VitalShark | [vitalshark.ru](https://vitalshark.ru) |
| Donater | [donater.shop](http://donater.shop) |
| Holdik | [holdik.ru](http://holdik.ru) |

## Возможности

- 👤 Просмотр профиля и баланса
- 📦 Управление товарами — просмотр, создание, редактирование, удаление
- 💬 Чаты с покупателями и отправка сообщений
- 🤖 Авто-ответчик на ключевые слова
- 📋 Просмотр заказов
- 🔔 Уведомления о новых сообщениях в Telegram
- 🌐 Поддержка русского и английского языков

## Установка

**1. Клонируй репозиторий**
```
git clone https://github.com/Human001User/VHD-Universal
cd VHD-Universal
```

**2. Установи зависимости**
```
pip install -r requirements.txt
```
или запусти `install.bat` (Windows)

**3. Запусти бота**
```
python bot.py
```
или запусти `start.bat` (Windows)

При первом запуске бот попросит ввести:
- `access_token` от vitalshark.ru holdik.ru donater.shop
- Токен Telegram бота (получить у [@BotFather](https://t.me/BotFather))
- Ваш Telegram ID (узнать у [@userinfobot](https://t.me/userinfobot))

## Как получить access_token

1. Войдите на [vitalshark.ru](https://vitalshark.ru) [holdik.ru](https://holdik.ru) [donater.shop](https://donater.shop)
2. Откройте DevTools (`F12`) → вкладка **Application** → **Cookies**
3. Скопируйте значение `access_token`

## Требования

- Python 3.10+
- Аккаунт на одной из поддерживаемых платформ
- Telegram бот ([@BotFather](https://t.me/BotFather))

## Конфиг

После первого запуска настройки сохраняются в `bot_settings/config.json`.  
Этот файл содержит ваши токены — **не публикуйте его**.

## Лицензия

MIT

---

Если вам удобно пользоваться VHD-Universal, не забудьте поставить ⭐ звезду ⭐ данному проекту в правом верхнем углу GitHub-страницы (нужно быть авторизованным в свой аккаунт) :)
