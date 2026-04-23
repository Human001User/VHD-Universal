"""Simple i18n — RU / EN strings."""

STRINGS = {
    "ru": {
        # общее
        "back": "◀️ Назад",
        "cancel": "❌ Отмена",
        "error": "❌ Ошибка: {}",
        "not_authorized": "❌ Не авторизован",
        "token_expired": "❌ Токен VitalShark истёк!\n\nОбновите access_token в bot_settings/config.json",
        # выбор языка
        "choose_lang": "🌐 Выберите язык / Choose language:",
        "lang_set": "✅ Язык установлен: Русский",
        # старт / токен
        "welcome": (
            "👋 Добро пожаловать в <b>VHD-Universal</b>!\n\n"
            "Введите ваш <b>access_token</b> от vitalshark.ru\n\n"
            "Как получить токен:\n"
            "1. Войдите на vitalshark.ru donater.shop holdik.ru\n"
            "2. Откройте DevTools (F12) → Application → Cookies\n"
            "3. Скопируйте значение <code>access_token</code>"
        ),
        "token_invalid": "❌ Неверный токен. Попробуйте ещё раз:",
        "token_error": "❌ Ошибка подключения: {}\n\nПопробуйте ещё раз:",
        "token_ok": "✅ Авторизован как <b>{}</b>!\n\nВведите токен Telegram бота\n(получить у @BotFather командой /newbot):",
        "tg_token_ok": "✅ Telegram бот настроен!\n\n⚠️ <b>Перезапустите бота</b> (Ctrl+C → python bot.py)\nчтобы применить новый токен.",
        "new_token_prompt": "🔑 Введите новый <b>access_token</b>:",
        # главное меню
        "main_menu": "🏠 <b>Главное меню</b>\nVHD-Universal",
        "btn_profile": "👤 Профиль",
        "btn_chats": "💬 Чаты",
        "btn_autoresponse": "🤖 Авто-ответчик",
        "btn_my_goods": "📦 Мои товары",
        "btn_create_lot": "➕ Создать лот",
        "btn_orders": "📋 Заказы",
        "btn_settings": "⚙️ Настройки",
        # товары
        "goods_empty": "📦 <b>Мои товары</b>\n\nТоваров нет.",
        "goods_title": "📦 <b>Мои товары</b>\n",
        "good_edit_title_prompt": "✏️ Введите новое <b>название</b>:",
        "good_edit_desc_prompt": "📄 Введите новое <b>описание</b>:",
        "good_edit_price_prompt": "💰 Введите новую <b>цену</b> (число):",
        "good_edit_old_price_prompt": "🏷 Введите <b>цену до скидки</b> (0 — убрать):",
        "good_updated": "✅ Товар обновлён!",
        "good_delete_confirm": "🗑 Удалить товар <b>{}</b>?\n\nЭто действие необратимо!",
        "good_deleted": "✅ Товар удалён.",
        "good_not_found": "❌ Товар не найден.",
        "btn_edit_title": "✏️ Изменить название",
        "btn_edit_desc": "📄 Изменить описание",
        "btn_edit_price": "💰 Изменить цену",
        "btn_edit_old_price": "🏷 Цена до скидки",
        "btn_delete": "🗑 Удалить товар",
        "btn_yes_delete": "✅ Да, удалить",
        # создание лота
        "create_lot_app": "➕ <b>Создание лота</b>\n\nВыберите приложение/игру:",
        "create_lot_cat": "📂 Выберите категорию:",
        "create_lot_method": "📦 Выберите способ передачи товара:",
        "create_lot_options": "🎛 Выберите параметры (можно несколько):",
        "create_lot_title": "📝 Введите <b>название</b> лота (мин. 5 символов):",
        "create_lot_desc": "📄 Введите <b>описание</b> лота:",
        "create_lot_price": "💰 Введите <b>цену</b> (число, например: 99):",
        "create_lot_old_price": "🏷 Введите <b>цену до скидки</b> (или <code>0</code> чтобы пропустить):",
        "create_lot_photos": "🖼 Отправьте <b>фото</b> товара (до 5 штук).\nКогда закончите — нажмите <b>Готово</b>.",
        "create_lot_confirm": "📦 <b>Проверьте данные лота:</b>\n\nНазвание: <b>{title}</b>\nОписание: {desc}\nЦена: <b>{price} ₽</b>\n",
        "create_lot_old_price_line": "Цена до скидки: <b>{} ₽</b>\n",
        "create_lot_ok": "✅ Лот <b>{}</b> создан!\nЦена: {} ₽",
        "create_lot_error": "❌ Ошибка создания лота: {}",
        "btn_create_confirm": "✅ Создать",
        "price_invalid": "❌ Введите число, например: 99",
        # заказы
        "orders_empty": "📋 <b>Заказы</b>\n\nЗаказов нет.",
        "orders_title": "📋 <b>Заказы</b>\n",
        # чаты
        "chats_empty": "💬 <b>Чаты</b>\n\nАктивных диалогов нет.",
        "chats_title": "💬 <b>Чаты</b>\n",
        "chat_reply_prompt": "✉️ Введите сообщение для отправки:",
        "chat_reply_ok": "✅ Сообщение отправлено!",
        "btn_reply": "✉️ Ответить",
        "btn_back_chats": "◀️ К чатам",
        # авто-ответчик
        "ar_title": "🤖 <b>Авто-ответчик</b>\nСтатус: {}\n",
        "ar_enabled": "✅ Включён",
        "ar_disabled": "❌ Выключен",
        "ar_commands": "<b>Команды:</b>",
        "ar_no_commands": "Команд нет. Нажмите «Добавить команду».",
        "ar_status_changed": "✅ Статус изменён",
        "ar_no_commands_alert": "Команд нет. Добавьте первую!",
        "ar_delete_list": "🗑 Нажмите на команду чтобы удалить её:",
        "ar_deleted": "✅ Команда «{}» удалена",
        "ar_trigger_prompt": "📝 Введите <b>триггер</b> (слово/фраза):\n\nНапример: <code>привет</code>",
        "ar_reply_prompt": "✉️ Введите <b>ответ</b> на этот триггер:",
        "ar_added": "✅ Добавлено:\n<code>{}</code> → {}",
        "btn_ar_status": "Статус: {}",
        "btn_ar_list": "📋 Список команд",
        "btn_ar_add": "➕ Добавить команду",
        # настройки
        "settings_title": "⚙️ <b>Настройки</b>",
        "btn_change_token": "🔑 Сменить access_token",
        "btn_notifications": "🔔 Уведомления",
        "btn_language": "🌐 Язык",
        "btn_proxy": "🌐 Прокси",
        "proxy_title": "🌐 <b>Прокси</b>\nСтатус: {}\nАдрес: <code>{}</code>",
        "proxy_enabled": "✅ Включён",
        "proxy_disabled": "❌ Выключен",
        "proxy_none": "не задан",
        "proxy_toggle": "Прокси: {}",
        "proxy_set_prompt": "✏️ Введите адрес прокси в формате:\n<code>host:port</code> или <code>user:pass@host:port</code>",
        "proxy_set_ok": "✅ Прокси сохранён: <code>{}</code>\n\n⚠️ Перезапустите бота для применения.",
        "proxy_clear_ok": "✅ Прокси удалён.\n\n⚠️ Перезапустите бота для применения.",
        "btn_proxy_set": "✏️ Задать адрес",
        "btn_proxy_clear": "🗑 Удалить прокси",
        "notif_title": "🔔 <b>Уведомления</b>",
        "notif_all": "Уведомления: {}",
        "notif_msg": "{} Новые сообщения",
        "notif_order": "{} Новые заказы",
        "notif_on": "✅ Вкл",
        "notif_off": "❌ Выкл",
        # уведомления
        "notify_new_message": "📩 <b>Новое сообщение</b>\n\nОт: <b>{}</b>\nТекст: {}",
    },
    "en": {
        # general
        "back": "◀️ Back",
        "cancel": "❌ Cancel",
        "error": "❌ Error: {}",
        "not_authorized": "❌ Not authorized",
        "token_expired": "❌ VitalShark token expired!\n\nUpdate access_token in bot_settings/config.json",
        # language
        "choose_lang": "🌐 Choose language / Выберите язык:",
        "lang_set": "✅ Language set: English",
        # start / token
        "welcome": (
            "👋 Welcome to <b>VHD-Universal</b>!\n\n"
            "Enter your <b>access_token</b> from vitalshark.ru\n\n"
            "How to get the token:\n"
            "1. Log in to vitalshark.ru\n"
            "2. Open DevTools (F12) → Application → Cookies\n"
            "3. Copy the value of <code>access_token</code>"
        ),
        "token_invalid": "❌ Invalid token. Try again:",
        "token_error": "❌ Connection error: {}\n\nTry again:",
        "token_ok": "✅ Logged in as <b>{}</b>!\n\nEnter your Telegram bot token\n(get it from @BotFather with /newbot):",
        "tg_token_ok": "✅ Telegram bot configured!\n\n⚠️ <b>Restart the bot</b> (Ctrl+C → python bot.py)\nto apply the new token.",
        "new_token_prompt": "🔑 Enter new <b>access_token</b>:",
        # main menu
        "main_menu": "🏠 <b>Main Menu</b>\nVHD-Universal",
        "btn_profile": "👤 Profile",
        "btn_chats": "💬 Chats",
        "btn_autoresponse": "🤖 Auto-reply",
        "btn_my_goods": "📦 My Listings",
        "btn_create_lot": "➕ Create Listing",
        "btn_orders": "📋 Orders",
        "btn_settings": "⚙️ Settings",
        # goods
        "goods_empty": "📦 <b>My Listings</b>\n\nNo listings yet.",
        "goods_title": "📦 <b>My Listings</b>\n",
        "good_edit_title_prompt": "✏️ Enter new <b>title</b>:",
        "good_edit_desc_prompt": "📄 Enter new <b>description</b>:",
        "good_edit_price_prompt": "💰 Enter new <b>price</b> (number):",
        "good_edit_old_price_prompt": "🏷 Enter <b>original price</b> (0 to remove):",
        "good_updated": "✅ Listing updated!",
        "good_delete_confirm": "🗑 Delete listing <b>{}</b>?\n\nThis cannot be undone!",
        "good_deleted": "✅ Listing deleted.",
        "good_not_found": "❌ Listing not found.",
        "btn_edit_title": "✏️ Edit title",
        "btn_edit_desc": "📄 Edit description",
        "btn_edit_price": "💰 Edit price",
        "btn_edit_old_price": "🏷 Original price",
        "btn_delete": "🗑 Delete listing",
        "btn_yes_delete": "✅ Yes, delete",
        # create lot
        "create_lot_app": "➕ <b>Create Listing</b>\n\nChoose app/game:",
        "create_lot_cat": "📂 Choose category:",
        "create_lot_method": "📦 Choose delivery method:",
        "create_lot_options": "🎛 Select options (multiple allowed):",
        "create_lot_title": "📝 Enter listing <b>title</b> (min. 5 chars):",
        "create_lot_desc": "📄 Enter listing <b>description</b>:",
        "create_lot_price": "💰 Enter <b>price</b> (number, e.g. 99):",
        "create_lot_old_price": "🏷 Enter <b>original price</b> (or <code>0</code> to skip):",
        "create_lot_photos": "🖼 Send <b>photos</b> of the item (up to 5).\nWhen done — press <b>Done</b>.",
        "create_lot_confirm": "📦 <b>Review your listing:</b>\n\nTitle: <b>{title}</b>\nDescription: {desc}\nPrice: <b>{price} ₽</b>\n",
        "create_lot_old_price_line": "Original price: <b>{} ₽</b>\n",
        "create_lot_ok": "✅ Listing <b>{}</b> created!\nPrice: {} ₽",
        "create_lot_error": "❌ Error creating listing: {}",
        "btn_create_confirm": "✅ Create",
        "price_invalid": "❌ Enter a number, e.g. 99",
        # orders
        "orders_empty": "📋 <b>Orders</b>\n\nNo orders yet.",
        "orders_title": "📋 <b>Orders</b>\n",
        # chats
        "chats_empty": "💬 <b>Chats</b>\n\nNo active chats.",
        "chats_title": "💬 <b>Chats</b>\n",
        "chat_reply_prompt": "✉️ Enter your message:",
        "chat_reply_ok": "✅ Message sent!",
        "btn_reply": "✉️ Reply",
        "btn_back_chats": "◀️ Back to chats",
        # auto-reply
        "ar_title": "🤖 <b>Auto-reply</b>\nStatus: {}\n",
        "ar_enabled": "✅ Enabled",
        "ar_disabled": "❌ Disabled",
        "ar_commands": "<b>Commands:</b>",
        "ar_no_commands": "No commands. Press «Add command».",
        "ar_status_changed": "✅ Status changed",
        "ar_no_commands_alert": "No commands. Add the first one!",
        "ar_delete_list": "🗑 Tap a command to delete it:",
        "ar_deleted": "✅ Command «{}» deleted",
        "ar_trigger_prompt": "📝 Enter <b>trigger</b> (word/phrase):\n\nExample: <code>hello</code>",
        "ar_reply_prompt": "✉️ Enter the <b>reply</b> for this trigger:",
        "ar_added": "✅ Added:\n<code>{}</code> → {}",
        "btn_ar_status": "Status: {}",
        "btn_ar_list": "📋 Command list",
        "btn_ar_add": "➕ Add command",
        # settings
        "settings_title": "⚙️ <b>Settings</b>",
        "btn_change_token": "🔑 Change access_token",
        "btn_notifications": "🔔 Notifications",
        "btn_language": "🌐 Language",
        "btn_proxy": "🌐 Proxy",
        "proxy_title": "🌐 <b>Proxy</b>\nStatus: {}\nAddress: <code>{}</code>",
        "proxy_enabled": "✅ Enabled",
        "proxy_disabled": "❌ Disabled",
        "proxy_none": "not set",
        "proxy_toggle": "Proxy: {}",
        "proxy_set_prompt": "✏️ Enter proxy address:\n<code>host:port</code> or <code>user:pass@host:port</code>",
        "proxy_set_ok": "✅ Proxy saved: <code>{}</code>\n\n⚠️ Restart the bot to apply.",
        "proxy_clear_ok": "✅ Proxy removed.\n\n⚠️ Restart the bot to apply.",
        "btn_proxy_set": "✏️ Set address",
        "btn_proxy_clear": "🗑 Remove proxy",
        "notif_title": "🔔 <b>Notifications</b>",
        "notif_all": "Notifications: {}",
        "notif_msg": "{} New messages",
        "notif_order": "{} New orders",
        "notif_on": "✅ On",
        "notif_off": "❌ Off",
        # notifications
        "notify_new_message": "📩 <b>New message</b>\n\nFrom: <b>{}</b>\nText: {}",
    }
}


def t(key: str, lang: str = "ru", *args) -> str:
    """Get translated string, fallback to RU."""
    s = STRINGS.get(lang, STRINGS["ru"]).get(key) or STRINGS["ru"].get(key, key)
    if args:
        return s.format(*args)
    return s
