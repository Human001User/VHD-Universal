from __future__ import annotations
import logging
from functools import wraps
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import load_config, save_config
from vhd_api.account import Account
from vhd_api.exceptions import UnauthorizedError
from . import keyboards as kb
from . import templates as tmpl
from .states import SetupStates, AutoResponseStates, CreateLotStates, EditLotStates, ChatReplyStates, ProxyStates
from .i18n import t

logger = logging.getLogger("vhd.handlers")
router = Router()

_account: Account | None = None


def get_account() -> Account | None:
    return _account


def set_account(acc: Account):
    global _account
    _account = acc


def _lang() -> str:
    return load_config().get("language", "ru")


def require_account(func):
    """Decorator: проверяет авторизацию перед выполнением callback-хендлера."""
    @wraps(func)
    async def wrapper(call: CallbackQuery, *args, acc: Account, **kwargs):
        try:
            acc.get_me()  # Проверяем токен
        except UnauthorizedError:
            lang = _lang()
            await call.answer(t("token_expired", lang), show_alert=True)
            return
        await call.answer()
        return await func(call, *args, acc=acc, **kwargs)
    return wrapper


# ─── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    cfg = load_config()
    lang = cfg.get("language", "")
    if not lang:
        await message.answer("🌐 Выберите язык / Choose language:", reply_markup=_lang_kb())
        await state.set_state(SetupStates.waiting_language)
        return
    if not cfg["vhd-universal-account"]["access_token"]:
        await message.answer(t("welcome", lang), parse_mode="HTML")
        await state.set_state(SetupStates.waiting_token)
        return
    await _show_main_menu(message)


def _lang_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🇷🇺 Русский", callback_data="set_lang:ru")
    b.button(text="🇬🇧 English", callback_data="set_lang:en")
    b.adjust(2)
    return b.as_markup()


@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_lang(call: CallbackQuery, state: FSMContext):
    lang = call.data.split(":")[1]
    cfg = load_config()
    cfg["language"] = lang
    save_config(cfg)
    await call.answer()
    await call.message.edit_text(t("lang_set", lang))
    if not cfg["vhd-universal-account"]["access_token"]:
        await call.message.answer(t("welcome", lang), parse_mode="HTML")
        await state.set_state(SetupStates.waiting_token)
    else:
        await _show_main_menu(call)


@router.callback_query(F.data == "change_language")
async def cb_change_language(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("🌐 Выберите язык / Choose language:", reply_markup=_lang_kb())


# ─── Токен ────────────────────────────────────────────────────────────────────

@router.message(SetupStates.waiting_token)
async def process_token(message: Message, state: FSMContext):
    lang = _lang()
    token = message.text.strip()
    try:
        acc = Account(access_token=token)
        profile = acc.get_me()
    except UnauthorizedError:
        await message.answer(t("token_invalid", lang))
        return
    except Exception as e:
        await message.answer(t("token_error", lang, e))
        return
    cfg = load_config()
    cfg["vhd-universal-account"]["access_token"] = token
    save_config(cfg)
    set_account(acc)
    await state.clear()
    logger.info(f"Авторизован как: {profile.name}")
    await message.answer(t("token_ok", lang, profile.name), parse_mode="HTML")
    await state.set_state(SetupStates.waiting_tg_token)


@router.message(SetupStates.waiting_tg_token)
async def process_tg_token(message: Message, state: FSMContext):
    lang = _lang()
    cfg = load_config()
    cfg["telegram"]["token"] = message.text.strip()
    cfg["telegram"]["admin_id"] = message.from_user.id
    save_config(cfg)
    await state.clear()
    await message.answer(t("tg_token_ok", lang), parse_mode="HTML")


# ─── Главное меню ─────────────────────────────────────────────────────────────

async def _show_main_menu(event: Message | CallbackQuery):
    lang = _lang()
    text = t("main_menu", lang)
    markup = kb.main_menu_kb(lang)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=markup, parse_mode="HTML")


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await _show_main_menu(call)


# ─── Профиль ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "profile")
@require_account
async def cb_profile(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    try:
        profile = acc.get_me()
        await call.message.edit_text(
            tmpl.profile_text(profile, lang),
            reply_markup=kb.back_kb(lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang))


# ─── Чаты ─────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "chats")
@require_account
async def cb_chats(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    try:
        chats = acc.get_chats()
        await call.message.edit_text(
            tmpl.chats_text(chats, lang),
            reply_markup=kb.chats_kb(chats, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang))


@router.callback_query(F.data.startswith("chat:"))
@require_account
async def cb_chat_open(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    chat_id = call.data.split(":", 1)[1]
    try:
        chats = acc.get_chats()
        chat = next((c for c in chats if c.id == chat_id), None)
        messages = acc.get_chat_messages(chat_id)
        profile = acc.profile or acc.get_me()
        await call.message.edit_text(
            tmpl.chat_messages_text(chat, messages, profile.id, lang),
            reply_markup=kb.chat_actions_kb(chat_id, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang, "chats"))


@router.callback_query(F.data.startswith("chat_reply:"))
async def cb_chat_reply(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    await call.answer()
    chat_id = call.data.split(":", 1)[1]
    await state.update_data(reply_chat_id=chat_id)
    await state.set_state(ChatReplyStates.waiting_message)
    await call.message.answer(t("chat_reply_prompt", lang), reply_markup=kb.back_kb(lang, "chats"))


@router.message(ChatReplyStates.waiting_message)
async def process_chat_reply(message: Message, state: FSMContext):
    lang = _lang()
    acc = get_account()
    data = await state.get_data()
    chat_id = data.get("reply_chat_id")
    await state.clear()
    try:
        acc.send_message(chat_id, message.text)
        await message.answer(t("chat_reply_ok", lang), reply_markup=kb.back_kb(lang, "chats"))
    except Exception as e:
        await message.answer(t("error", lang, e), reply_markup=kb.back_kb(lang, "chats"))


# ─── Авто-ответчик ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "autoresponse_menu")
async def cb_ar_menu(call: CallbackQuery):
    lang = _lang()
    await call.answer()
    cfg = load_config()
    await call.message.edit_text(
        tmpl.autoresponse_text(cfg["auto_response"]["commands"], cfg["auto_response"]["enabled"], lang),
        reply_markup=kb.autoresponse_menu_kb(cfg["auto_response"]["enabled"], lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "autoresponse_toggle")
async def cb_ar_toggle(call: CallbackQuery):
    lang = _lang()
    cfg = load_config()
    cfg["auto_response"]["enabled"] = not cfg["auto_response"]["enabled"]
    save_config(cfg)
    await call.answer(t("ar_status_changed", lang))
    await call.message.edit_text(
        tmpl.autoresponse_text(cfg["auto_response"]["commands"], cfg["auto_response"]["enabled"], lang),
        reply_markup=kb.autoresponse_menu_kb(cfg["auto_response"]["enabled"], lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "autoresponse_list")
async def cb_ar_list(call: CallbackQuery):
    lang = _lang()
    commands = load_config()["auto_response"]["commands"]
    if not commands:
        await call.answer(t("ar_no_commands_alert", lang), show_alert=True)
        return
    await call.answer()
    await call.message.edit_text(
        t("ar_delete_list", lang),
        reply_markup=kb.autoresponse_list_kb(commands, lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("ar_delete:"))
async def cb_ar_delete(call: CallbackQuery):
    lang = _lang()
    trigger = call.data.split(":", 1)[1]
    cfg = load_config()
    cfg["auto_response"]["commands"].pop(trigger, None)
    save_config(cfg)
    await call.answer(t("ar_deleted", lang, trigger))
    commands = cfg["auto_response"]["commands"]
    if not commands:
        await cb_ar_menu(call)
        return
    await call.message.edit_text(
        t("ar_delete_list", lang),
        reply_markup=kb.autoresponse_list_kb(commands, lang)
    )


@router.callback_query(F.data == "autoresponse_add")
async def cb_ar_add(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    await call.answer()
    await state.set_state(AutoResponseStates.waiting_trigger)
    await call.message.answer(
        t("ar_trigger_prompt", lang),
        parse_mode="HTML",
        reply_markup=kb.back_kb(lang, "autoresponse_menu")
    )


@router.message(AutoResponseStates.waiting_trigger)
async def process_ar_trigger(message: Message, state: FSMContext):
    lang = _lang()
    await state.update_data(trigger=message.text.strip().lower())
    await state.set_state(AutoResponseStates.waiting_reply)
    await message.answer(t("ar_reply_prompt", lang), parse_mode="HTML", reply_markup=kb.back_kb(lang, "autoresponse_menu"))


@router.message(AutoResponseStates.waiting_reply)
async def process_ar_reply(message: Message, state: FSMContext):
    lang = _lang()
    data = await state.get_data()
    trigger = data["trigger"]
    reply = message.text.strip()
    cfg = load_config()
    cfg["auto_response"]["commands"][trigger] = reply
    save_config(cfg)
    await state.clear()
    logger.info(f"Добавлена команда авто-ответа: «{trigger}»")
    await message.answer(
        t("ar_added", lang, trigger, reply),
        parse_mode="HTML",
        reply_markup=kb.back_kb(lang, "autoresponse_menu")
    )


# ─── Мои товары ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "my_goods")
@require_account
async def cb_my_goods(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    try:
        goods = acc.get_my_goods()
        await call.message.edit_text(
            tmpl.goods_text(goods, lang),
            reply_markup=kb.goods_kb(goods, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang))


@router.callback_query(F.data.startswith("good:"))
@require_account
async def cb_good_detail(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    good_id = call.data.split(":", 1)[1]
    try:
        # Сначала пробуем GET /goods/{id}, если 404 — ищем в списке своих товаров
        try:
            good = acc.get_good(good_id)
        except Exception:
            goods = acc.get_my_goods()
            good = next((g for g in goods if g.id == good_id), None)
            if not good:
                await call.message.edit_text(t("good_not_found", lang), reply_markup=kb.back_kb(lang, "my_goods"))
                return
        await call.message.edit_text(
            tmpl.good_detail_text(good, lang),
            reply_markup=kb.good_actions_kb(good_id, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang, "my_goods"))


# ─── Редактирование товара ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("good_edit:"))
async def cb_good_edit(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    await call.answer()
    parts = call.data.split(":")
    field, good_id = parts[1], parts[2]
    await state.update_data(edit_field=field, edit_good_id=good_id)
    await state.set_state(EditLotStates.waiting_value)
    prompts = {
        "title": t("good_edit_title_prompt", lang),
        "description": t("good_edit_desc_prompt", lang),
        "price": t("good_edit_price_prompt", lang),
        "old_price": t("good_edit_old_price_prompt", lang),
    }
    await call.message.answer(
        prompts.get(field, "✏️ Введите новое значение:"),
        parse_mode="HTML",
        reply_markup=kb.back_kb(lang, f"good:{good_id}")
    )


@router.message(EditLotStates.waiting_value)
async def process_good_edit(message: Message, state: FSMContext):
    lang = _lang()
    acc = get_account()
    data = await state.get_data()
    field, good_id = data["edit_field"], data["edit_good_id"]
    value = message.text.strip()
    await state.clear()

    kwargs = {}
    if field in ("price", "old_price"):
        try:
            parsed = float(value.replace(",", "."))
            kwargs["price" if field == "price" else "price_before_discount"] = parsed
        except ValueError:
            await message.answer(t("price_invalid", lang), reply_markup=kb.back_kb(lang, f"good:{good_id}"))
            return
    else:
        kwargs[field] = value

    try:
        good = acc.update_good(good_id, **kwargs)
        logger.info(f"Товар обновлён: {good.title} (поле: {field})")
        await message.answer(
            t("good_updated", lang) + "\n\n" + tmpl.good_detail_text(good, lang),
            reply_markup=kb.good_actions_kb(good_id, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(t("error", lang, e), reply_markup=kb.back_kb(lang, "my_goods"))


# ─── Удаление товара ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("good_delete:"))
@require_account
async def cb_good_delete(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    good_id = call.data.split(":", 1)[1]
    try:
        try:
            good = acc.get_good(good_id)
            title = good.title
        except Exception:
            goods = acc.get_my_goods()
            good = next((g for g in goods if g.id == good_id), None)
            title = good.title if good else good_id
        await call.message.edit_text(
            t("good_delete_confirm", lang, title),
            reply_markup=kb.confirm_delete_kb(good_id, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang, "my_goods"))


@router.callback_query(F.data.startswith("good_delete_confirm:"))
@require_account
async def cb_good_delete_confirm(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    good_id = call.data.split(":", 1)[1]
    try:
        acc.delete_good(good_id)
        logger.info(f"Товар удалён: id={good_id}")
        goods = acc.get_my_goods()
        await call.message.edit_text(
            t("good_deleted", lang) + "\n\n" + tmpl.goods_text(goods, lang),
            reply_markup=kb.goods_kb(goods, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang, "my_goods"))


# ─── Создать лот ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "create_lot")
@require_account
async def cb_create_lot(call: CallbackQuery, state: FSMContext, acc: Account, **_):
    lang = _lang()
    try:
        apps = acc.get_apps()
        await state.update_data(apps=apps)
        await call.message.edit_text(t("create_lot_app", lang), reply_markup=kb.apps_kb(apps, lang), parse_mode="HTML")
        await state.set_state(CreateLotStates.waiting_app)
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang))


@router.callback_query(F.data.startswith("lot_app:"), CreateLotStates.waiting_app)
async def cb_lot_app(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    idx = int(call.data.split(":")[1])
    await call.answer()
    data = await state.get_data()
    app = data["apps"][idx]
    await state.update_data(app_id=app["id"], app_slug=app["slug"])
    acc = get_account()
    try:
        cats = acc.get_app_categories(app["slug"])
        await state.update_data(categories=cats)
        await call.message.edit_text(t("create_lot_cat", lang), reply_markup=kb.categories_kb(cats, app["slug"], lang), parse_mode="HTML")
        await state.set_state(CreateLotStates.waiting_category)
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang))


@router.callback_query(F.data.startswith("lot_cat:"), CreateLotStates.waiting_category)
async def cb_lot_cat(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    idx = int(call.data.split(":")[1])
    await call.answer()
    data = await state.get_data()
    cat = data["categories"][idx]
    await state.update_data(category_id=cat["id"], cat_slug=cat["slug"])
    await call.message.answer(t("create_lot_title", lang), parse_mode="HTML")
    await state.set_state(CreateLotStates.waiting_title)


@router.message(CreateLotStates.waiting_title)
async def process_lot_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer(t("create_lot_desc", _lang()), parse_mode="HTML")
    await state.set_state(CreateLotStates.waiting_description)


@router.message(CreateLotStates.waiting_description)
async def process_lot_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await message.answer(t("create_lot_price", _lang()), parse_mode="HTML")
    await state.set_state(CreateLotStates.waiting_price)


@router.message(CreateLotStates.waiting_price)
async def process_lot_price(message: Message, state: FSMContext):
    lang = _lang()
    try:
        price = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer(t("price_invalid", lang))
        return
    await state.update_data(price=price)
    await message.answer(t("create_lot_old_price", lang), parse_mode="HTML")
    await state.set_state(CreateLotStates.waiting_old_price)


@router.message(CreateLotStates.waiting_old_price)
async def process_lot_old_price(message: Message, state: FSMContext):
    lang = _lang()
    try:
        old_price = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer(t("price_invalid", lang))
        return
    await state.update_data(old_price=old_price if old_price > 0 else None)
    data = await state.get_data()
    summary = t("create_lot_confirm", lang).format(
        title=data["title"], desc=data["description"][:100], price=data["price"]
    )
    if data.get("old_price"):
        summary += t("create_lot_old_price_line", lang, data["old_price"])
    await message.answer(summary, reply_markup=kb.confirm_lot_kb(lang), parse_mode="HTML")


@router.callback_query(F.data == "lot_confirm")
async def cb_lot_confirm(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    acc = get_account()
    data = await state.get_data()
    await state.clear()
    await call.answer()
    try:
        fields_data = acc.get_category_fields(data["app_slug"], data["cat_slug"])
        # obtain_methods[0].id — метод получения товара (обязательный)
        obtain_method_id = fields_data[0]["id"] if fields_data else None
        good = acc.create_good(
            app_id=data["app_id"],
            category_id=data["category_id"],
            title=data["title"],
            description=data["description"],
            price=data["price"],
            fields=[],
            obtain_method_id=obtain_method_id,
            price_before_discount=data.get("old_price"),
        )
        logger.info(f"Создан лот: {good.title} — {good.price} ₽")
        await call.message.edit_text(
            t("create_lot_ok", lang, good.title, good.price),
            reply_markup=kb.back_kb(lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("create_lot_error", lang, e), reply_markup=kb.back_kb(lang))


# ─── Заказы ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "orders")
@require_account
async def cb_orders(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    try:
        orders = acc.get_orders()
        await call.message.edit_text(
            tmpl.orders_text(orders, lang),
            reply_markup=kb.orders_kb(orders, lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang))


@router.callback_query(F.data.startswith("order:"))
@require_account
async def cb_order_detail(call: CallbackQuery, acc: Account, **_):
    lang = _lang()
    order_id = call.data.split(":", 1)[1]
    try:
        orders = acc.get_orders()
        order = next((o for o in orders if o.get("id") == order_id), None)
        if not order:
            await call.answer(t("good_not_found", lang), show_alert=True)
            return
        await call.message.edit_text(
            tmpl.order_detail_text(order, lang),
            reply_markup=kb.back_kb(lang, "orders"),
            parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(t("error", lang, e), reply_markup=kb.back_kb(lang, "orders"))


# ─── Настройки ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "settings_menu")
async def cb_settings(call: CallbackQuery):
    lang = _lang()
    await call.answer()
    await call.message.edit_text(t("settings_title", lang), reply_markup=kb.settings_kb(lang), parse_mode="HTML")


@router.callback_query(F.data == "change_token")
async def cb_change_token(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    await call.answer()
    await state.set_state(SetupStates.waiting_token)
    await call.message.answer(t("new_token_prompt", lang), parse_mode="HTML")


# ─── Уведомления ──────────────────────────────────────────────────────────────

async def _render_notifications(call: CallbackQuery):
    lang = _lang()
    cfg = load_config()
    await call.message.edit_text(t("notif_title", lang), reply_markup=kb.notifications_kb(cfg, lang), parse_mode="HTML")


@router.callback_query(F.data == "notifications_menu")
async def cb_notifications(call: CallbackQuery):
    await call.answer()
    await _render_notifications(call)


@router.callback_query(F.data == "notif_toggle_all")
async def cb_notif_toggle_all(call: CallbackQuery):
    cfg = load_config()
    cfg["tg_logging"]["enabled"] = not cfg["tg_logging"]["enabled"]
    save_config(cfg)
    await call.answer()
    await _render_notifications(call)


@router.callback_query(F.data == "notif_toggle_msg")
async def cb_notif_toggle_msg(call: CallbackQuery):
    cfg = load_config()
    cfg["tg_logging"]["events"]["new_message"] = not cfg["tg_logging"]["events"]["new_message"]
    save_config(cfg)
    await call.answer()
    await _render_notifications(call)


@router.callback_query(F.data == "notif_toggle_order")
async def cb_notif_toggle_order(call: CallbackQuery):
    cfg = load_config()
    cfg["tg_logging"]["events"]["new_order"] = not cfg["tg_logging"]["events"]["new_order"]
    save_config(cfg)
    await call.answer()
    await _render_notifications(call)


# ─── Прокси ───────────────────────────────────────────────────────────────────

def _proxy_menu_text(cfg: dict, lang: str) -> str:
    acc_cfg = cfg["vhd-universal-account"]
    enabled = acc_cfg.get("proxy_enabled", False)
    proxy = acc_cfg.get("proxy") or t("proxy_none", lang)
    status = t("proxy_enabled", lang) if enabled else t("proxy_disabled", lang)
    return t("proxy_title", lang, status, proxy)


@router.callback_query(F.data == "proxy_menu")
async def cb_proxy_menu(call: CallbackQuery):
    lang = _lang()
    await call.answer()
    cfg = load_config()
    acc_cfg = cfg["vhd-universal-account"]
    await call.message.edit_text(
        _proxy_menu_text(cfg, lang),
        reply_markup=kb.proxy_kb(acc_cfg.get("proxy_enabled", False), bool(acc_cfg.get("proxy")), lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "proxy_toggle")
async def cb_proxy_toggle(call: CallbackQuery):
    lang = _lang()
    cfg = load_config()
    acc_cfg = cfg["vhd-universal-account"]
    if not acc_cfg.get("proxy"):
        await call.answer(t("proxy_set_prompt", lang)[:200], show_alert=True)
        return
    acc_cfg["proxy_enabled"] = not acc_cfg.get("proxy_enabled", False)
    save_config(cfg)
    await call.answer()
    await call.message.edit_text(
        _proxy_menu_text(cfg, lang),
        reply_markup=kb.proxy_kb(acc_cfg["proxy_enabled"], bool(acc_cfg.get("proxy")), lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "proxy_set")
async def cb_proxy_set(call: CallbackQuery, state: FSMContext):
    lang = _lang()
    await call.answer()
    await state.set_state(ProxyStates.waiting_proxy)
    await call.message.answer(t("proxy_set_prompt", lang), parse_mode="HTML", reply_markup=kb.back_kb(lang, "proxy_menu"))


@router.message(ProxyStates.waiting_proxy)
async def process_proxy(message: Message, state: FSMContext):
    lang = _lang()
    proxy = message.text.strip()
    cfg = load_config()
    cfg["vhd-universal-account"]["proxy"] = proxy
    cfg["vhd-universal-account"]["proxy_enabled"] = True
    save_config(cfg)
    await state.clear()
    logger.info(f"Прокси обновлён: {proxy}")
    await message.answer(t("proxy_set_ok", lang, proxy), parse_mode="HTML", reply_markup=kb.back_kb(lang, "proxy_menu"))


@router.callback_query(F.data == "proxy_clear")
async def cb_proxy_clear(call: CallbackQuery):
    lang = _lang()
    cfg = load_config()
    cfg["vhd-universal-account"]["proxy"] = ""
    cfg["vhd-universal-account"]["proxy_enabled"] = False
    save_config(cfg)
    await call.answer()
    await call.message.edit_text(
        t("proxy_clear_ok", lang),
        reply_markup=kb.back_kb(lang, "proxy_menu"),
        parse_mode="HTML"
    )
