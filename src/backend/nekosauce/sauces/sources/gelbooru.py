from enum import Enum

import re
import urllib.parse

import grequests
import requests

import validators

from nekosauce.sauces import sources
from nekosauce.sauces.models import Sauce, Source


def paginate(iterable, limit: int) -> list:
    return [(iterable[i : i + limit], i) for i in range(0, len(iterable), limit)]


class GelbooruFetcher(sources.BaseFetcher):
    site_name: str = "Gelbooru"
    base_url: str = "https://gelbooru.com"
    source: Source = Source.objects.get(name="Gelbooru")

    @property
    def last_page(self) -> str:
        return int(self.last_sauce.source_site_id)

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request(
            "GET", f"/index.php?page=dapi&q=index&json=1&s=post&id={id}"
        )

    def get_sauce(self, id: str) -> Sauce:
        qs = Sauce.objects.filter(tags__overlap=[f"gelbooru:post:id:{id}"])

        if qs.exists():
            return qs[0]

        r = grequests.map(self.get_sauce_request(id))[0]
        post = r.json()

        return self.get_sauce_from_response(post)

    def get_new_sauce_from_response(self, post: dict) -> Sauce:
        site_urls = [
            f"https://gelbooru.com/index.php?page=post&s=view&id={post['id']}"
        ] + (
            post.get("source").split(" ") if validators.url(post.get("source")) else []
        )

        sauce = Sauce(
            title=f"Artwork from Gelbooru #{post['id']} - {post['image']}",
            site_urls=site_urls,
            api_urls=[
                self.get_url(
                    f"/index.php?page=dapi&q=index&json=1&s=post&id={post['id']}"
                )
            ],
            file_urls=[post.get("file_url")]
            if post.get("file_url")
            else post["source"].split(" "),
            source=self.source,
            source_site_id=post["id"],
            tags=sources.get_tags(site_urls)
            + [f"gelbooru:tag:name:{tag}" for tag in post["tags"].split(" ")],
            is_nsfw=post["rating"] in ["questionable", "explicit"],
            height=post["height"],
            width=post["width"],
        )

        return sauce

    def get_sauce_from_response(self, post: dict) -> Sauce:
        sauce = Sauce.objects.filter(
            tags__overlap=[f"gelbooru:post:id:{post['id']}"]
        ).first()

        if sauce:
            return sauce

        sauce = self.get_new_sauce_from_response(post)
        sauce.save()

        return sauce

    def get_file_url(self, id: str) -> str:
        qs = Source.objects.filter(tags__overlap=[f"gelbooru:post:id:{id}"])

        if qs.exists():
            return qs[0].file_urls[0]

        sauce = self.get_sauce(id)
        return sauce.file_urls[0]

    def get_sauces_iter(self, start_from=None):
        count = grequests.map(
            [self.request("GET", "/index.php?page=dapi&q=index&json=1&s=post&limit=1")]
        )[0].json()["post"][0]["id"]
        last = 0

        if isinstance(start_from, Sauce):
            last = int(start_from.source_site_id)
        elif isinstance(start_from, int):
            last = start_from

        for index, response in grequests.imap_enumerated(
            [
                self.request(
                    "GET",
                    f"/index.php?page=dapi&q=index&json=1&s=post&limit=100&tags=id:<{page + 100}",
                )
                for page in range(last, count, 100)
            ],
            size=self.async_reqs,
        ):
            new_sauces = []
            for post in response.json()["post"]:
                new_sauces.append(self.get_new_sauce_from_response(post))

            Sauce.objects.bulk_create(
                new_sauces,
                ignore_conflicts=True,
            )
            yield from new_sauces

            for sauce in new_sauces:
                if sauce.source_site_id == str(count):
                    return


class GelbooruDownloader(sources.BaseFetcher):
    fetcher = GelbooruFetcher
    site_name = "Gelbooru"

    def check_url(self, url: str) -> bool:
        return re.match(r"^https://[a-zA-Z0-9-]+\.gelbooru\.com/", url) is not None

    def get_sauce_id(url: str) -> str:
        return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["id"][0]

    def download_request(self, url: str):
        if urllib.parse.urlparse(url).netloc == "gelbooru.com":
            url = self.fetcher.get_file_url(DanbooruDownloader.get_sauce_id(url))

        return grequests.get(url)

    def download(self, url: str) -> bytes:
        if urllib.parse.urlparse(url).netloc == "gelbooru.com":
            url = self.fetcher.get_file_url(DanbooruDownloader.get_sauce_id(url))

        r = requests.get(url)
        r.raise_for_status()

        return r.content


class GelbooruTagger(sources.BaseTagger):
    source = "gelbooru"
    source_domain = "gelbooru.com"
    resources = ["post", "tag"]

    get_resource = lambda self, url: urllib.parse.parse_qs(url.query).get(
        "page", ["unknown"]
    )[0]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: urllib.parse.parse_qs(url.query).get(
        "id", ["unknown"]
    )[0]

    def check_url(self, url: str) -> bool:
        return (
            url.startswith("https://gelbooru.com")
            and self.get_resource(url) in resources
            and self.get_value(url) != "unknown"
        )
