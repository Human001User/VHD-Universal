from aiogram.fsm.state import State, StatesGroup


class SetupStates(StatesGroup):
    waiting_language = State()
    waiting_token = State()
    waiting_tg_token = State()


class AutoResponseStates(StatesGroup):
    waiting_trigger = State()
    waiting_reply = State()


class CreateLotStates(StatesGroup):
    waiting_app = State()
    waiting_category = State()
    waiting_obtain_method = State()
    waiting_options = State()
    waiting_title = State()
    waiting_description = State()
    waiting_price = State()
    waiting_old_price = State()
    waiting_photos = State()


class EditLotStates(StatesGroup):
    waiting_value = State()


class ChatReplyStates(StatesGroup):
    waiting_message = State()


class ProxyStates(StatesGroup):
    waiting_proxy = State()
