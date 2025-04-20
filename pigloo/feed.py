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
    image: HttpUrl


class Feed(BaseModel):
    id: UUID4
    user: User
    service: Service
    media: Media
    progress: int | None
    datetime: AwareDatetime