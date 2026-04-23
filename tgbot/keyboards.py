from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .i18n import t


def main_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_profile", lang), callback_data="profile")
    kb.button(text=t("btn_chats", lang), callback_data="chats")
    kb.button(text=t("btn_autoresponse", lang), callback_data="autoresponse_menu")
    kb.button(text=t("btn_my_goods", lang), callback_data="my_goods")
    kb.button(text=t("btn_create_lot", lang), callback_data="create_lot")
    kb.button(text=t("btn_orders", lang), callback_data="orders")
    kb.button(text=t("btn_settings", lang), callback_data="settings_menu")
    kb.adjust(2)
    return kb.as_markup()


def back_kb(lang: str = "ru", callback: str = "main_menu") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("back", lang), callback_data=callback)
    return kb.as_markup()


def autoresponse_menu_kb(enabled: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    status = t("ar_enabled", lang) if enabled else t("ar_disabled", lang)
    kb.button(text=t("btn_ar_status", lang, status), callback_data="autoresponse_toggle")
    kb.button(text=t("btn_ar_list", lang), callback_data="autoresponse_list")
    kb.button(text=t("btn_ar_add", lang), callback_data="autoresponse_add")
    kb.button(text=t("back", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def autoresponse_list_kb(commands: dict, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for trigger in commands:
        kb.button(text=f"🗑 {trigger}", callback_data=f"ar_delete:{trigger}")
    kb.button(text=t("back", lang), callback_data="autoresponse_menu")
    kb.adjust(1)
    return kb.as_markup()


def chats_kb(chats: list, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for chat in chats:
        if chat.type == "private" and chat.user:
            label = f"💬 {chat.user.name}"
            if chat.unread_count > 0:
                label += f" ({chat.unread_count}🔴)"
            kb.button(text=label, callback_data=f"chat:{chat.id}")
    kb.button(text=t("back", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def chat_actions_kb(chat_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_reply", lang), callback_data=f"chat_reply:{chat_id}")
    kb.button(text=t("btn_back_chats", lang), callback_data="chats")
    kb.adjust(1)
    return kb.as_markup()


def settings_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_change_token", lang), callback_data="change_token")
    kb.button(text=t("btn_notifications", lang), callback_data="notifications_menu")
    kb.button(text=t("btn_proxy", lang), callback_data="proxy_menu")
    kb.button(text=t("btn_language", lang), callback_data="change_language")
    kb.button(text=t("back", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def proxy_kb(enabled: bool, has_proxy: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    status = t("proxy_enabled", lang) if enabled else t("proxy_disabled", lang)
    kb.button(text=t("proxy_toggle", lang, status), callback_data="proxy_toggle")
    kb.button(text=t("btn_proxy_set", lang), callback_data="proxy_set")
    if has_proxy:
        kb.button(text=t("btn_proxy_clear", lang), callback_data="proxy_clear")
    kb.button(text=t("back", lang), callback_data="settings_menu")
    kb.adjust(1)
    return kb.as_markup()


def notifications_kb(cfg: dict, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    tg = cfg["tg_logging"]
    on = t("notif_on", lang)
    off = t("notif_off", lang)
    enabled_status = on if tg["enabled"] else off
    msg_icon = "✅" if tg["events"]["new_message"] else "❌"
    order_icon = "✅" if tg["events"]["new_order"] else "❌"
    kb.button(text=t("notif_all", lang, enabled_status), callback_data="notif_toggle_all")
    kb.button(text=t("notif_msg", lang, msg_icon), callback_data="notif_toggle_msg")
    kb.button(text=t("notif_order", lang, order_icon), callback_data="notif_toggle_order")
    kb.button(text=t("back", lang), callback_data="settings_menu")
    kb.adjust(1)
    return kb.as_markup()


def goods_kb(goods: list, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for g in goods[:15]:
        status_icon = "✅" if g.status == "active" else "⏸"
        # используем slug для API запросов, id как fallback
        key = g.slug or g.id
        kb.button(text=f"{status_icon} {g.title[:30]}", callback_data=f"good:{key}")
    kb.button(text=t("btn_create_lot", lang), callback_data="create_lot")
    kb.button(text=t("back", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def good_actions_kb(good_key: str, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_edit_title", lang), callback_data=f"good_edit:title:{good_key}")
    kb.button(text=t("btn_edit_desc", lang), callback_data=f"good_edit:description:{good_key}")
    kb.button(text=t("btn_edit_price", lang), callback_data=f"good_edit:price:{good_key}")
    kb.button(text=t("btn_edit_old_price", lang), callback_data=f"good_edit:old_price:{good_key}")
    kb.button(text=t("btn_delete", lang), callback_data=f"good_delete:{good_key}")
    kb.button(text=t("back", lang), callback_data="my_goods")
    kb.adjust(1)
    return kb.as_markup()


def confirm_delete_kb(good_key: str, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_yes_delete", lang), callback_data=f"good_delete_confirm:{good_key}")
    kb.button(text=t("cancel", lang), callback_data=f"good:{good_key}")
    kb.adjust(2)
    return kb.as_markup()


def apps_kb(apps: list, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, app in enumerate(apps[:15]):
        kb.button(text=app["title"], callback_data=f"lot_app:{i}")
    kb.button(text=t("cancel", lang), callback_data="main_menu")
    kb.adjust(2)
    return kb.as_markup()


def categories_kb(categories: list, app_slug: str, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, cat in enumerate(categories[:15]):
        kb.button(text=cat["title"], callback_data=f"lot_cat:{i}")
    kb.button(text=t("cancel", lang), callback_data="main_menu")
    kb.adjust(2)
    return kb.as_markup()


def obtain_methods_kb(methods: list, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, m in enumerate(methods[:10]):
        kb.button(text=m["title"], callback_data=f"lot_method:{i}")
    kb.button(text=t("cancel", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def options_kb(values: list, selected: list, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, v in enumerate(values[:20]):
        icon = "✅" if v in selected else "◻️"
        kb.button(text=f"{icon} {v}", callback_data=f"lot_opt:{i}")
    kb.button(text=t("btn_create_confirm", lang), callback_data="lot_opts_done")
    kb.button(text=t("cancel", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def photos_kb(count: int, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if count > 0:
        kb.button(text=f"✅ Готово ({count} фото)", callback_data="lot_photos_done")
    kb.button(text=t("cancel", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_create_confirm", lang), callback_data="lot_confirm")
    kb.button(text=t("cancel", lang), callback_data="main_menu")
    kb.adjust(2)
    return kb.as_markup()


def orders_kb(orders: list, lang: str = "ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for o in orders[:10]:
        status = o.get("status", "")
        icon = "🟢" if status == "completed" else "🟡" if status == "pending" else "🔵"
        title = o.get("good", {}).get("title", "Order")[:25]
        kb.button(text=f"{icon} {title}", callback_data=f"order:{o['id']}")
    kb.button(text=t("back", lang), callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()
