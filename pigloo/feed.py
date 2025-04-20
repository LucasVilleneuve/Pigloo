from pydantic import BaseModel, UUID4, AwareDatetime, HttpUrl


class Service(BaseModel):
    id: UUID4
    name: str


class User(BaseModel):
    id: UUID4
    name: str
    service: Service


class Media(BaseModel):
    id: UUID4
    name: str
    service: Service
    max_progress: int
    url: HttpUrl
    image: HttpUrl
    type: str  # e.g. "anime", "manga", etc.


class Feed(BaseModel):
    id: UUID4
    user: User
    service: Service
    media: Media
    progress: int | None
    datetime: AwareDatetime