from enum import Enum
from dataclasses import dataclass
import typing


SOURCES = (
    "sources.danbooru.DanbooruFetcher",
)


class SauceType(Enum):
    ART = "art"
    ANIME = "anime"
    MANGA = "manga"


@dataclass
class OriginalPoster:
    site_urls: typing.List[str]
    api_urls: typing.List[str]
    name: str
    sauce_name: str
    sauce_site_id: str


@dataclass
class Sauce:
    site_urls: typing.List[str]
    api_urls: typing.List[str]
    file_url: str
    sauce_type: SauceType = SauceType.ART
    sauce_name: str
    sauce_site_id: str
    original_poster: OriginalPoster


class BaseSauceFetcher:

    def list_sauces(self, page: int = 0) -> typing.List[Sauce]:
        raise NotImplementedError("You need to implement the `.list_sauces()` method.")
