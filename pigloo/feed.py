from pydantic import UUID4, AwareDatetime, BaseModel, HttpUrl


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
    format: str  # e.g. "TV", "Movie", etc.

    def build_progress_str(self, progress: int) -> str:
        return f"{progress} of {self.max_progress}"


class Anime(Media):
    def __init__(self, **data):
        super().__init__(**data)

    def build_progress_str(self, progress: int) -> str:
        return f"{progress} of {self.max_progress} episodes"


class Manga(Media):
    def __init__(self, **data):
        super().__init__(**data)

    def build_progress_str(self, progress: int) -> str:
        return f"{progress} of {self.max_progress} chapters"


class Feed(BaseModel):
    id: UUID4
    user: User
    service: Service
    media: Media
    progress: int | None
    datetime: AwareDatetime
