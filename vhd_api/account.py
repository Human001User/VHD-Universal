from __future__ import annotations
import requests
from typing import Optional
from .types import (
    UserProfile, Balance, UserStats,
    Chat, ChatUser, LastMessage,
    ChatMessage, Good, GoodApp, GoodCategory
)
from .exceptions import UnauthorizedError, NotFoundError, RequestError


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Поддерживаемые площадки
PLATFORMS = {
    "vitalshark": {
        "name": "VitalShark",
        "domain": "vitalshark.ru",
        "base_url": "https://vitalshark.ru/api/v1",
    },
    "donater": {
        "name": "Donater",
        "domain": "donater.shop",
        "base_url": "https://donater.shop/api/v1",
    },
    "holdik": {
        "name": "Holdik",
        "domain": "holdik.ru",
        "base_url": "https://holdik.ru/api/v1",
    },
}


class Account:
    """Клиент для работы с API торговой площадки."""

    def __init__(
        self,
        access_token: str,
        platform: str = "vitalshark",
        proxy: Optional[str] = None,
        timeout: int = 30,
    ):
        if platform not in PLATFORMS:
            raise ValueError(f"Неизвестная площадка: {platform}. Доступны: {', '.join(PLATFORMS)}")
        self.access_token = access_token
        self.platform = platform
        self.platform_info = PLATFORMS[platform]
        self.timeout = timeout
        self._base_url = self.platform_info["base_url"]
        domain = self.platform_info["domain"]
        origin = f"https://{domain}"

        self._session = requests.Session()
        self._session.cookies.set("access_token", access_token, domain=domain)
        self._session.headers.update({
            "User-Agent": DEFAULT_UA,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": origin,
            "Referer": f"{origin}/",
            "Authorization": f"Bearer {access_token}",
        })
        if proxy:
            self._session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

        self.profile: Optional[UserProfile] = None

    # ─── Внутренние методы ────────────────────────────────────────────────────

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self._base_url}{path}"
        r = self._session.request(method, url, timeout=self.timeout, **kwargs)
        if r.status_code == 401:
            raise UnauthorizedError("Неверный или истёкший access_token")
        if r.status_code == 404:
            raise NotFoundError(f"Не найдено: {path}")
        if not r.ok:
            raise RequestError(r.status_code, r.text[:300])
        if r.status_code == 204 or not r.content:
            return {}
        return r.json()

    def _get(self, path: str, params: dict = None) -> dict:
        return self._request("GET", path, params=params)

    def _post(self, path: str, data: dict = None) -> dict:
        return self._request("POST", path, json=data or {})

    # ─── Профиль ──────────────────────────────────────────────────────────────

    def get_me(self) -> UserProfile:
        """Получить профиль текущего пользователя."""
        d = self._get("/users/me")
        bal = d.get("balance", {})
        stats = d.get("stats", {})
        self.profile = UserProfile(
            id=d["id"],
            name=d["name"],
            is_verified=d.get("is_verified", False),
            picture_url=d.get("picture_url"),
            balance=Balance(
                available=bal.get("available", "0"),
                withdrawable=bal.get("withdrawable", "0"),
                hold=bal.get("hold", "0"),
                frozen=bal.get("frozen", "0"),
            ),
            stats=UserStats(
                rating=stats.get("rating", "0"),
                reviews_count=stats.get("reviews_count", 0),
                reviews_positive=stats.get("reviews_positive", 0),
                reviews_negative=stats.get("reviews_negative", 0),
                orders_success=stats.get("orders_success", 0),
            ),
            unread_chats=d.get("unread_chats", 0),
            support_chat_id=d.get("support_chat", {}).get("id", "") if d.get("support_chat") else "",
        )
        return self.profile

    # ─── Чаты ─────────────────────────────────────────────────────────────────

    def get_chats(self, cursor: str = None) -> list[Chat]:
        """Получить список чатов."""
        params = {}
        if cursor:
            params["cursor"] = cursor
        d = self._get("/chats", params=params)
        result = []
        for item in d.get("items", []):
            lm_data = item.get("last_message")
            lm = None
            if lm_data:
                lm = LastMessage(
                    id=lm_data["id"],
                    type=lm_data["type"],
                    created_at=lm_data["created_at"],
                    text=lm_data.get("text"),
                    picture_url=lm_data.get("picture_url"),
                )
            u_data = item.get("user")
            user = None
            if u_data:
                user = ChatUser(
                    id=u_data["id"],
                    name=u_data["name"],
                    is_verified=u_data.get("is_verified", False),
                    picture_url=u_data.get("picture_url"),
                    is_banned=u_data.get("is_banned", False),
                )
            result.append(Chat(
                id=item["id"],
                type=item["type"],
                user=user,
                unread_count=item.get("unread_count", 0),
                last_message=lm,
            ))
        return result

    def get_chat_messages(self, chat_id: str, cursor: str = None) -> list[ChatMessage]:
        """Получить сообщения чата."""
        params = {}
        if cursor:
            params["cursor"] = cursor
        d = self._get(f"/chats/{chat_id}/messages", params=params)
        result = []
        for item in d.get("items", []):
            result.append(ChatMessage(
                id=item["id"],
                type=item["type"],
                created_at=item["created_at"],
                text=item.get("text"),
                picture_url=item.get("picture_url"),
                sender_id=item.get("sender", {}).get("id") if item.get("sender") else None,
            ))
        return result

    def send_message(self, chat_id: str, text: str) -> ChatMessage:
        """Отправить сообщение в чат."""
        d = self._post(f"/chats/{chat_id}/messages", {"text": text})
        return ChatMessage(
            id=d["id"],
            type=d.get("type", "manual"),
            created_at=d["created_at"],
            text=d.get("text"),
        )

    def mark_chat_read(self, chat_id: str) -> None:
        """Пометить чат как прочитанный."""
        self._post(f"/chats/{chat_id}/read")

    # ─── Товары ───────────────────────────────────────────────────────────────

    def get_my_goods(self, cursor: str = None) -> list[Good]:
        """Получить свои товары."""
        if not self.profile:
            self.get_me()
        params = {}
        if cursor:
            params["cursor"] = cursor
        d = self._get(f"/users/{self.profile.id}/goods", params=params)
        return self._parse_goods(d.get("items", []))

    def get_good(self, good_slug: str) -> Good:
        """Получить товар по slug."""
        return self._parse_good(self._get(f"/goods/{good_slug}"))

    def create_good(
        self,
        app_id: str,
        category_id: str,
        title: str,
        description: str,
        price: float,
        fields: list[dict],
        pictures: list[str] = None,
        price_before_discount: float = None,
        obtain_method_id: str = None,
    ) -> Good:
        """Создать новый лот."""
        payload = {
            "app_id": app_id,
            "category_id": category_id,
            "title": title,
            "description": description,
            "price": str(price),
            "fields": fields,
        }
        if obtain_method_id:
            payload["obtain_method_id"] = obtain_method_id
        if price_before_discount:
            payload["price_before_discount"] = str(price_before_discount)
        if pictures:
            payload["pictures"] = pictures
        d = self._post("/goods", payload)
        # API может вернуть неполный объект после создания — пробуем распарсить,
        # если не хватает полей — возвращаем минимальный Good с тем что есть
        try:
            return self._parse_good(d)
        except (KeyError, TypeError):
            return Good(
                id=d.get("id", ""),
                slug=d.get("slug", ""),
                title=d.get("title", title),
                price=d.get("price", str(price)),
                price_before_discount=d.get("price_before_discount"),
                app=None,
                category=None,
                status=d.get("status"),
                description=d.get("description", description),
            )

    def update_good(
        self,
        good_slug: str,
        title: str = None,
        description: str = None,
        price: float = None,
        price_before_discount: float = None,
    ) -> Good:
        """Обновить лот по slug."""
        payload = {}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if price is not None:
            payload["price"] = str(price)
        if price_before_discount is not None:
            payload["price_before_discount"] = str(price_before_discount) if price_before_discount > 0 else None
        d = self._request("PATCH", f"/goods/{good_slug}", json=payload)
        try:
            return self._parse_good(d)
        except (KeyError, TypeError):
            return Good(
                id=d.get("id", ""),
                slug=good_slug,
                title=d.get("title", title or ""),
                price=d.get("price", str(price or "")),
                price_before_discount=d.get("price_before_discount"),
                app=None, category=None,
                status=d.get("status"),
                description=d.get("description", description or ""),
            )

    def delete_good(self, good_slug: str) -> None:
        """Удалить лот по slug."""
        self._request("DELETE", f"/goods/{good_slug}")

    def get_orders(self, cursor: str = None) -> list[dict]:
        """Получить список заказов."""
        params = {}
        if cursor:
            params["cursor"] = cursor
        d = self._get("/orders", params=params)
        return d.get("items", [])

    def get_apps(self) -> list[dict]:
        """Получить список приложений/игр."""
        d = self._get("/apps")
        return d.get("items", [])

    def get_app_categories(self, app_slug: str) -> list[dict]:
        """Получить категории приложения через GET /apps/{slug}."""
        d = self._get(f"/apps/{app_slug}")
        return d.get("goods_categories", [])

    def get_category_fields(self, app_slug: str, category_slug: str) -> list[dict]:
        """Получить поля категории через GET /apps/{slug}."""
        cats = self.get_app_categories(app_slug)
        cat = next((c for c in cats if c.get("slug") == category_slug), None)
        if not cat:
            return []
        # Возвращаем obtain_methods как "fields" для совместимости
        return cat.get("obtain_methods", [])

    # ─── Парсеры ──────────────────────────────────────────────────────────────

    def _parse_good(self, d: dict) -> Good:
        app_d = d.get("app")
        cat_d = d.get("category")
        return Good(
            id=d["id"],
            slug=d.get("slug", ""),
            title=d["title"],
            price=d["price"],
            price_before_discount=d.get("price_before_discount"),
            app=GoodApp(
                id=app_d["id"],
                slug=app_d["slug"],
                title=app_d["title"],
                icon_url=app_d.get("icon_url"),
            ) if app_d else None,
            category=GoodCategory(
                id=cat_d["id"],
                slug=cat_d["slug"],
                title=cat_d["title"],
            ) if cat_d else None,
            status=d.get("status"),
            description=d.get("description"),
        )

    def _parse_goods(self, items: list) -> list[Good]:
        return [self._parse_good(i) for i in items]
