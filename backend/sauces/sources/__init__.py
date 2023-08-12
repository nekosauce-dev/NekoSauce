from enum import Enum
from dataclasses import dataclass
import os
import typing


def get_fetcher(name: str):
    match name.lower():
        case "danbooru":
            from sauces.sources.danbooru import DanbooruFetcher

            return DanbooruFetcher
    return None


class SauceType(Enum):
    ART = "art"
    ANIME = "anime"
    MANGA = "manga"


@dataclass
class Artist:
    site_urls: typing.List[str]
    api_urls: typing.List[str]
    names: typing.List[str]
    sauce_name: str
    sauce_site_id: str


@dataclass
class Sauce:
    site_urls: typing.List[str]
    api_urls: typing.List[str]
    file_url: str
    sauce_name: str
    sauce_site_id: str
    artist: Artist
    height: int
    width: int
    sauce_type: SauceType = SauceType.ART


class BaseSauceFetcher:
    def __init__(self, iter_from=0, async_reqs=10):
        self.credentials = {
            "user": os.getenv(f"SAUCE_{self.site_name.upper()}_USER"),
            "pass": os.getenv(f"SAUCE_{self.site_name.upper()}_PASS"),
        }
        self.current_iter_page = iter_from
        self.loaded_iter_items = []
        self.current_iter_item = 0
        self.iter_from = iter_from
        self.async_reqs = async_reqs

    def get_artist(self, id) -> Artist:
        raise NotImplementedError("You need to implement the `.get_artist()` method.")

    def list_sauces(self, page: int = 0) -> typing.List[Sauce]:
        raise NotImplementedError("You need to implement the `.list_sauces()` method.")

    def __iter__(self):
        self.current_iter_page = self.iter_from
        return self

    def __next__(self):
        sauces = self.list_sauces(
            self.current_iter_page, reqs=self.async_reqs, async_reqs=self.async_reqs
        )
        self.current_iter_page += 1
        return sauces
