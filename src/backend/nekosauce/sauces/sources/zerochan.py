import typing
import urllib.parse

import grequests
import requests

from nekosauce.sauces import sources
from nekosauce.sauces.utils import paginate
from nekosauce.sauces.models import Sauce


class ZerochanFetcher(sources.BaseFetcher):
    site_name = "Zerochan"
    base_url = "https://zerochan.net"

    def get_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def request(self, method: str, path: str) -> grequests.AsyncRequest:
        return grequests.request(
            method,
            self.get_url(path),
            headers={
                "User-Agent": "NekoSauce",
            },
        )

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request("GET", f"{id}?json")

    def _get_new_sauce_from_response(self, post: dict) -> Sauce:
        site_urls = [
            f"https://zerochan.net/{post['id']}",
        ] + ([post["source"]] if post["source"] else [])

        sauce = Sauce(
            site_urls=site_urls,
            api_urls=[
                f"https://zerochan.net/{post['id']}?json",
            ],
            file_urls=[
                f"https://s1.zerochan.net/{urllib.parse.quote(post['tag'].replace(' ', '.'))}.full.{post['id']}.jpg",
            ],
            source_id=self.source_id,
            source_site_id=str(post["id"]),
            tags=sources.get_tags(site_urls)
            + [
                f"zerochan:tag:name:{urllib.parse.quote_plus(tag)}"
                for tag in post["tags"]
            ],
            is_nsfw=None,
            height=post.get("height", 0),
            width=post.get("width", 0),
        )

        return sauce

    def get_sauces_iter(
        self, start_from: int = 0, chunk_size: int = 1024
    ) -> typing.Iterator[Sauce]:
        last_id = grequests.map([self.request("GET", "/?json&p=1&l=1")])[0].json()[
            "items"
        ][0]["id"]

        if isinstance(start_from, Sauce):
            page = int(start_from.source_site_id)
        else:
            page = last_id + int(start_from) if start_from is not None else 1
    
        for offset in range(page - 1, last_id + 1, 250):
            response = requests.get(f"https://zerochan.net/?json&l=250&o={offset}", headers={
                "User-Agent": "NekoSauce"
            })

            if response is None:
                return

            new_sauces = [
                self._get_new_sauce_from_response(
                    post,
                )
                for post in response.json()["items"]
            ]
            Sauce.objects.bulk_create(
                new_sauces,
                ignore_conflicts=True,
            )
            yield from new_sauces


class ZerochanDownloader(sources.BaseFetcher):
    fetcher = ZerochanFetcher
    site_name = "Zerochan"

    def check_url(self, url: str) -> bool:
        return url.startswith("https://s1.zerochan.net/")

    def get_sauce_id(url: str) -> str:
        return urllib.parse.urlparse(url).path.split("/")[1].split("?")[0]

    def download_request(self, url: str):
        return grequests.get(url)

    def download(self, url: str) -> bytes:
        r = requests.get(url)
        r.raise_for_status()

        return r.content


class ZerochanTagger(sources.BaseTagger):
    source = "zerochan"
    source_domain = "zerochan.net"
    resources = ["post"]

    get_resource = lambda self, url: "post"
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[1].split("?")[0]

    def check_url(self, url: str) -> bool:
        return url.startswith("https://zerochan.net/")
