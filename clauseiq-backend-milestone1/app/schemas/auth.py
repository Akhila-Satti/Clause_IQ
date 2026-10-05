from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str

    full_name: str = ""

    age: int | None = None
    occupation: str | None = None
    income: str | None = None
    location: str | None = None

    personalization_consent: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

    age: int | None
    occupation: str | None
    income: str | None
    location: str | None

    personalization_consent: bool


class AuthResponse(BaseModel):
    message: str
    access_token: str
    user: UserResponse