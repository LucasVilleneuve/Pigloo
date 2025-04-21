import discord
from pydantic import UUID4, AwareDatetime, BaseModel, HttpUrl, model_validator
from typing_extensions import Self


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

    def build_progress_str(self, progress: int) -> str:  # FIXME: progress can be None
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


class FeedStatus(BaseModel):
    """Represents the status of a user's activity related to media.

    Provides a base structure for specific status types with a color and label.
    """

    color: int = discord.Colour.default().value
    label: str


class WatchingStatus(FeedStatus):
    color: int = discord.Colour.green().value
    label: str = "Watching"


class ReadingStatus(FeedStatus):
    color: int = discord.Colour.green().value
    label: str = "Reading"


class CompletedStatus(FeedStatus):
    color: int = discord.Colour.blue().value
    label: str = "Completed"


class DroppedStatus(FeedStatus):
    color: int = discord.Colour.brand_red().value
    label: str = "Dropped"


class PausedStatus(FeedStatus):
    color: int = discord.Colour.gold().value
    label: str = "Paused"


class PlanToWatchStatus(FeedStatus):
    color: int = discord.Colour.greyple().value
    label: str = "Plans to watch"


class PlanToReadStatus(FeedStatus):
    color: int = discord.Colour.greyple().value
    label: str = "Plans to read"


class RewatchingStatus(FeedStatus):
    color: int = discord.Colour.dark_green().value
    label: str = "Rewatching"


class RereadingStatus(FeedStatus):
    color: int = discord.Colour.dark_green().value
    label: str = "Rereading"


class Feed(BaseModel):
    id: UUID4
    user: User
    service: Service
    media: Media
    progress: int | None
    datetime: AwareDatetime
    status: FeedStatus

    @model_validator(mode="after")
    def validate_status(self) -> Self:
        label = self.status.label

        if label is None:
            raise ValueError("Label cannot be None")

        first_word = label.split()[0].upper()

        if first_word in ("READ", "READING", "WATCHED", "WATCHING"):
            self.status = WatchingStatus() if isinstance(self.media, Anime) else ReadingStatus()
        elif first_word in ("PLANS", "PLAN", "PLAN_TO_WATCH", "PLAN_TO_READ"):
            self.status = PlanToWatchStatus() if isinstance(self.media, Anime) else PlanToReadStatus()
        elif first_word == "COMPLETED":
            self.status = CompletedStatus()
        elif first_word == "DROPPED":
            self.status = DroppedStatus()
        elif first_word in ("PAUSED", "ON-HOLD", "ON_HOLD"):
            self.status = PausedStatus()
        elif first_word in ("REWATCHED", "REWATCHING", "RE-WATCHING", "RE-WATCHED"):  # TODO This doesn't exist for MAL
            self.status = RewatchingStatus()
        elif first_word in ("REREAD", "REREADING", "RE-READING", "RE-READ"):  # TODO This doesn't exist for MAL
            self.status = RereadingStatus()
        else:
            raise ValueError(f"Cannot convert '{label}' to a FeedStatus")

        return self
