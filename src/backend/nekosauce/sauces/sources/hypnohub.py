from enum import Enum

import re
import urllib.parse

import grequests
import requests

import validators

from nekosauce.sauces import sources
from nekosauce.sauces.utils import paginate
from nekosauce.sauces.models import Sauce


class HypnoHubFetcher(sources.BaseFetcher):
    site_name: str = "HypnoHub"
    base_url: str = "https://hypnohub.net"

    last_page = property(lambda self: int(self.last_sauce.source_site_id))

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request(
            "GET", f"/index.php?page=dapi&q=index&json=1&s=post&id={id}"
        )

    def get_sauce(self, id: str) -> Sauce:
        qs = Sauce.objects.filter(tags__overlap=[f"hypnohub:post:id:{id}"])

        if qs.exists():
            return qs[0]

        r = grequests.map(self.get_sauce_request(id))[0]
        post = r.json()

        return self.get_sauce_from_response(post)

    def get_new_sauce_from_response(self, post: dict) -> Sauce:
        site_urls = [
            f"https://hypnohub.net/index.php?page=post&s=view&id={post['id']}"
        ]

        sauce = Sauce(
            site_urls=site_urls,
            api_urls=[
                f"https://hypnohub.net/index.php?page=dapi&q=index&json=1&s=post&id={post['id']}"
            ],
            file_urls=[post.get("file_url")],
            source_id=self.source_id,
            source_site_id=post["id"],
            tags=sources.get_tags(site_urls)
            + [f"hypnohub:tag:name:{tag}" for tag in post["tags"].split(" ")],
            is_nsfw=post["rating"] in ["questionable", "explicit"],
            height=post["height"] if post["height"] is not None else 0,
            width=post["width"] if post["width"] is not None else 0,
        )

        return sauce

    def get_sauce_from_response(self, post: dict) -> Sauce:
        sauce = Sauce.objects.filter(
            tags__overlap=[f"hypnohub:post:id:{post['id']}"]
        ).first()

        if sauce:
            return sauce

        sauce = self.get_new_sauce_from_response(post)
        sauce.save()

        return sauce

    def get_file_url(self, id: str) -> str:
        qs = Sauce.objects.filter(tags__overlap=[f"hypnohub:post:id:{id}"])

        if qs.exists():
            return qs[0].file_urls[0]

        sauce = self.get_sauce(id)
        return sauce.file_urls[0]

    def get_sauces_iter(self, chunk_size: int = 1024, start_from=None):
        count = grequests.map(
            [self.request("GET", "/index.php?page=dapi&q=index&json=1&s=post&limit=1")]
        )[0].json()[0]["id"]
        last = 0

        if isinstance(start_from, Sauce):
            last = int(start_from.source_site_id)
        elif isinstance(start_from, int):
            last = start_from
        else:
            last = int(start_from) if start_from is not None else 0

        reqs = [
            self.request(
                "GET",
                f"/index.php?page=dapi&q=index&json=1&s=post&limit=100&tags=id:<{page + 100}",
            )
            for page in range(last, count, 100)
        ]
        req_chunks = paginate(reqs, chunk_size)

        if len(req_chunks) == 0:
            return

        while True:
            for index, response in grequests.imap_enumerated(
                req_chunks[0],
                size=self.async_reqs,
            ):
                if response is None:
                    return

                new_sauces = []
                for post in response.json():
                    new_sauces.append(self.get_new_sauce_from_response(post))

                Sauce.objects.bulk_create(
                    new_sauces,
                    ignore_conflicts=True,
                )
                yield from new_sauces

                for sauce in new_sauces:
                    if sauce.source_site_id == str(count):
                        return

            del req_chunks[0]

            if len(req_chunks) == 0:
                break


class HypnoHubDownloader(sources.BaseDownloader):
    fetcher = HypnoHubFetcher
    site_name = "HypnoHub"

    def check_url(self, url: str) -> bool:
        return url.startswith("https://hypnohub.com/")

    def get_sauce_id(url: str) -> str:
        return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["id"][0]

    def download_request(self, url: str):
        return grequests.get(url)

    def download(self, url: str) -> bytes:
        r = requests.get(url)
        r.raise_for_status()

        return r.content


class HypnoHubTagger(sources.BaseTagger):
    source = "hypnohub"
    source_domain = "hypnohub.net"
    resources = ["post", "tag"]

    get_resource = lambda self, url: urllib.parse.parse_qs(url.query).get(
        "page", ["unknown"]
    )[0]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: urllib.parse.parse_qs(url.query).get(
        "id", ["unknown"]
    )[0]

    def check_url(self, url: str) -> bool:
        try:
            parsed_url = urllib.parse.urlparse(url)
            return (
                url.startswith("https://hypnohub.net")
                and self.get_resource(parsed_url) in self.resources
                and self.get_value(parsed_url) != "unknown"
                and self.check_resources(self.get_resource(parsed_url), False)
            )
        except Exception as e:
            return False