from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Balance:
    available: str
    withdrawable: str
    hold: str
    frozen: str


@dataclass
class UserStats:
    rating: str
    reviews_count: int
    reviews_positive: int
    reviews_negative: int
    orders_success: int


@dataclass
class UserProfile:
    id: str
    name: str
    is_verified: bool
    picture_url: Optional[str]
    balance: Balance
    stats: UserStats
    unread_chats: int
    support_chat_id: str


@dataclass
class ChatUser:
    id: str
    name: str
    is_verified: bool
    picture_url: Optional[str]
    is_banned: bool


@dataclass
class LastMessage:
    id: str
    type: str
    created_at: str
    text: Optional[str] = None
    picture_url: Optional[str] = None


@dataclass
class Chat:
    id: str
    type: str  # private, notifications, support
    user: Optional[ChatUser]
    unread_count: int
    last_message: Optional[LastMessage]


@dataclass
class ChatMessage:
    id: str
    type: str
    created_at: str
    text: Optional[str] = None
    picture_url: Optional[str] = None
    sender_id: Optional[str] = None


@dataclass
class GoodCategory:
    id: str
    slug: str
    title: str


@dataclass
class GoodApp:
    id: str
    slug: str
    title: str
    icon_url: Optional[str]


@dataclass
class Good:
    id: str
    slug: str
    title: str
    price: str
    price_before_discount: Optional[str]
    app: Optional[GoodApp]
    category: Optional[GoodCategory]
    status: Optional[str] = None
    description: Optional[str] = None
