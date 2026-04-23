from vhd_api.types import UserProfile, Chat, ChatMessage, Good
from typing import List
from .i18n import t


def profile_text(p: UserProfile, lang: str = "ru") -> str:
    try:
        stars = "⭐" * round(float(p.stats.rating))
    except (ValueError, TypeError):
        stars = ""
    verified = "✅" if p.is_verified else "❌"
    if lang == "en":
        return (
            f"👤 <b>VitalShark Profile</b>\n\n"
            f"🏷 Name: <b>{p.name}</b>\n"
            f"✔️ Verified: {verified}\n\n"
            f"💰 <b>Balance</b>\n"
            f"  Available: <b>{p.balance.available} ₽</b>\n"
            f"  Withdrawable: <b>{p.balance.withdrawable} ₽</b>\n"
            f"  Hold: <b>{p.balance.hold} ₽</b>\n\n"
            f"📊 <b>Stats</b>\n"
            f"  Rating: <b>{p.stats.rating}</b> {stars}\n"
            f"  Sales: <b>{p.stats.orders_success}</b>\n"
            f"  Reviews: <b>{p.stats.reviews_count}</b> "
            f"(👍 {p.stats.reviews_positive} / 👎 {p.stats.reviews_negative})\n"
            f"  Unread chats: <b>{p.unread_chats}</b>"
        )
    return (
        f"👤 <b>Профиль VitalShark</b>\n\n"
        f"🏷 Имя: <b>{p.name}</b>\n"
        f"✔️ Верификация: {verified}\n\n"
        f"💰 <b>Баланс</b>\n"
        f"  Доступно: <b>{p.balance.available} ₽</b>\n"
        f"  К выводу: <b>{p.balance.withdrawable} ₽</b>\n"
        f"  Холд: <b>{p.balance.hold} ₽</b>\n\n"
        f"📊 <b>Статистика</b>\n"
        f"  Рейтинг: <b>{p.stats.rating}</b> {stars}\n"
        f"  Продаж: <b>{p.stats.orders_success}</b>\n"
        f"  Отзывов: <b>{p.stats.reviews_count}</b> "
        f"(👍 {p.stats.reviews_positive} / 👎 {p.stats.reviews_negative})\n"
        f"  Непрочитанных чатов: <b>{p.unread_chats}</b>"
    )


def chats_text(chats: List[Chat], lang: str = "ru") -> str:
    private = [c for c in chats if c.type == "private"]
    if not private:
        return t("chats_empty", lang)
    lines = [t("chats_title", lang)]
    for c in private:
        name = c.user.name if c.user else ("Unknown" if lang == "en" else "Неизвестный")
        unread = f" 🔴 {c.unread_count}" if c.unread_count > 0 else ""
        last = ""
        if c.last_message and c.last_message.text:
            last = f"\n   └ {c.last_message.text[:50]}"
        lines.append(f"• <b>{name}</b>{unread}{last}")
    return "\n".join(lines)


def chat_messages_text(chat: Chat, messages: List[ChatMessage], my_id: str, lang: str = "ru") -> str:
    name = chat.user.name if chat and chat.user else "Chat"
    you = "You" if lang == "en" else "Вы"
    media = "[media]" if lang == "en" else "[медиа]"
    no_msgs = f"💬 <b>{'Chat with' if lang == 'en' else 'Диалог с'} {name}</b>\n\n{'No messages.' if lang == 'en' else 'Сообщений нет.'}"
    lines = [f"💬 <b>{'Chat with' if lang == 'en' else 'Диалог с'} {name}</b>\n"]
    for msg in reversed(messages[:10]):
        if msg.type != "manual":
            continue
        who = you if msg.sender_id == my_id else name
        text = msg.text or media
        lines.append(f"<b>{who}:</b> {text[:200]}")
    return "\n".join(lines) if len(lines) > 1 else no_msgs


def goods_text(goods: List[Good], lang: str = "ru") -> str:
    if not goods:
        return t("goods_empty", lang)
    lines = [t("goods_title", lang)]
    for g in goods[:15]:
        app = g.app.title if g.app else "—"
        cat = g.category.title if g.category else "—"
        status_icon = "✅" if g.status == "active" else "⏸"
        lines.append(f"{status_icon} <b>{g.title[:40]}</b>\n  {app} / {cat} — <b>{g.price} ₽</b>")
    return "\n".join(lines)


def good_detail_text(g: Good, lang: str = "ru") -> str:
    app = g.app.title if g.app else "—"
    cat = g.category.title if g.category else "—"
    if lang == "en":
        status_map = {"active": "✅ Active", "inactive": "⏸ Inactive", "sold": "💸 Sold"}
    else:
        status_map = {"active": "✅ Активен", "inactive": "⏸ Неактивен", "sold": "💸 Продан"}
    status = status_map.get(g.status or "", g.status or "—")
    text = (
        f"📦 <b>{g.title}</b>\n\n"
        f"🎮 {'Game' if lang == 'en' else 'Игра'}: {app}\n"
        f"📂 {'Category' if lang == 'en' else 'Категория'}: {cat}\n"
        f"💰 {'Price' if lang == 'en' else 'Цена'}: <b>{g.price} ₽</b>\n"
    )
    if g.price_before_discount:
        label = "Original price" if lang == "en" else "До скидки"
        text += f"🏷 {label}: <s>{g.price_before_discount} ₽</s>\n"
    text += f"📊 {'Status' if lang == 'en' else 'Статус'}: {status}\n"
    if g.description:
        label = "Description" if lang == "en" else "Описание"
        text += f"\n📄 {label}:\n{g.description[:300]}"
    return text


def orders_text(orders: list, lang: str = "ru") -> str:
    if not orders:
        return t("orders_empty", lang)
    lines = [t("orders_title", lang)]
    if lang == "en":
        status_map = {"completed": "🟢 Completed", "pending": "🟡 Pending", "cancelled": "🔴 Cancelled"}
    else:
        status_map = {"completed": "🟢 Выполнен", "pending": "🟡 В ожидании", "cancelled": "🔴 Отменён"}
    for o in orders[:10]:
        status = status_map.get(o.get("status", ""), o.get("status", "—"))
        title = o.get("good", {}).get("title", "—")[:30]
        price = o.get("price", "—")
        lines.append(f"• <b>{title}</b>\n  {status} — <b>{price} ₽</b>")
    return "\n".join(lines)


def order_detail_text(o: dict, lang: str = "ru") -> str:
    if lang == "en":
        status_map = {"completed": "🟢 Completed", "pending": "🟡 Pending", "cancelled": "🔴 Cancelled"}
        labels = {"good": "Item", "buyer": "Buyer", "price": "Price", "status": "Status", "date": "Date"}
    else:
        status_map = {"completed": "🟢 Выполнен", "pending": "🟡 В ожидании", "cancelled": "🔴 Отменён"}
        labels = {"good": "Товар", "buyer": "Покупатель", "price": "Цена", "status": "Статус", "date": "Дата"}
    status = status_map.get(o.get("status", ""), o.get("status", "—"))
    title = o.get("good", {}).get("title", "—")
    buyer = o.get("buyer", {}).get("name", "—") if o.get("buyer") else "—"
    date = o.get("created_at", "—")[:10]
    return (
        f"📋 <b>{'Order' if lang == 'en' else 'Заказ'}</b>\n\n"
        f"{labels['good']}: <b>{title}</b>\n"
        f"{labels['buyer']}: <b>{buyer}</b>\n"
        f"{labels['price']}: <b>{o.get('price', '—')} ₽</b>\n"
        f"{labels['status']}: {status}\n"
        f"{labels['date']}: {date}"
    )


def autoresponse_text(commands: dict, enabled: bool, lang: str = "ru") -> str:
    status = t("ar_enabled", lang) if enabled else t("ar_disabled", lang)
    lines = [t("ar_title", lang, status)]
    if commands:
        lines.append(t("ar_commands", lang))
        for trigger, reply in commands.items():
            lines.append(f"• <code>{trigger}</code> → {reply[:50]}")
    else:
        lines.append(t("ar_no_commands", lang))
    return "\n".join(lines)


def new_message_notify(chat: Chat, msg: ChatMessage, lang: str = "ru") -> str:
    name = chat.user.name if chat.user else ("Unknown" if lang == "en" else "Неизвестный")
    text = msg.text or ("[media]" if lang == "en" else "[медиа]")
    return t("notify_new_message", lang, name, text[:300])
