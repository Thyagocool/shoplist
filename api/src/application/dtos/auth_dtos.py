from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class RegisterInput:
    name: str
    email: str
    password: str


@dataclass
class LoginInput:
    email: str
    password: str


@dataclass
class TokenOutput:
    access_token: str
    refresh_token: str
    token_type: str = field(default="bearer")


@dataclass
class UserOutput:
    id: UUID
    name: str
    email: str
