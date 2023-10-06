import re
import io
import typing
import urllib.parse

from django.db.models import Q

from bs4 import BeautifulSoup

import grequests
import requests

import validators

from nekosauce.sauces import sources
from nekosauce.sauces.utils import paginate
from nekosauce.sauces.models import Sauce


class EshuushuuFetcher(sources.BaseFetcher):
    site_name = "E-shuushuu"
    base_url = "https://e-shuushuu.net"

    last_page = property(lambda self: self.last_sauce.source_site_id)

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request("GET", f"/image/{id}/")

    def _get_sauces_in_page(self, html: str):
        soup = BeautifulSoup(html, "html.parser")

        image_blocks = soup.find_all(**{"class": "image_block"})

        for block in image_blocks:
            site_urls = [
                "https://e-shuushuu.net"
                + block.find(href=re.compile(r"^/image/[0-9]+/$")).get("href")
            ]
            yield Sauce(
                width=0,
                height=0,
                source_id=self.source_id,
                source_site_id=block.find(href=re.compile(r"^/image/[0-9]+/$"))
                .get("href")
                .split("/")[-2],
                is_nsfw=None,
                tags=sources.get_tags(site_urls)
                + [
                    f"e-shuushuu:tag:name:{urllib.parse.quote_plus(tag.text)}"
                    for tag in block.find_all(href=re.compile(r"/tags/[0-9]+"))
                ]
                + [
                    f"e-shuushuu:tag:id:{tag.get('href').split('/')[-1]}"
                    for tag in block.find_all(href=re.compile(r"/tags/[0-9]+"))
                ],
                file_urls=[
                    "https://e-shuushuu.net"
                    + block.find(**{"class": "thumb_image"}).get("href")
                ],
                site_urls=site_urls,
                api_urls=[],
            )

    def get_file_url(self, id: str) -> str:
        qs = Sauce.objects.filter(tags__overlap=[f"e-shuushuu:post:id:{id}"])

        if qs.exists():
            return qs[0].file_urls[0]

        sauce = self.get_sauce(id)
        return sauce.file_urls[0]

    def get_sauces_iter(
        self, chunk_size: int = 1024, start_from=None
    ) -> typing.Iterator[Sauce]:
        greatest_id = list(
            self._get_sauces_in_page(
                list(grequests.map([self.request("GET", "/")]))[0].text
            )
        )[0].source_site_id

        reqs = [
            self.request("GET", f"/?page={p}")
            for p in range(
                1,
                greatest_id // 15
                if not start_from
                else greatest_id // 15 - int(start_from.source_site_id) // 15
                if isinstance(start_from, Sauce)
                else int(start_from),
            )
        ]
        reqs.reverse()

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

                Sauce.objects.bulk_create(
                    self._get_sauces_in_page(response.content),
                    ignore_conflicts=True,
                )
                yield from new_sauces

            del req_chunks[0]

            if len(req_chunks) == 0:
                break


class EshuushuuDownloader(sources.BaseFetcher):
    fetcher = EshuushuuFetcher
    site_name = "E-shuushuu"

    def check_url(self, url: str) -> bool:
        return url.startswith("https://e-shuushuu.net")

    def download_request(self, url: str):
        return grequests.get(url)

    def download(self, url: str) -> bytes:
        r = requests.get(url)
        r.raise_for_status()

        return r.content


class EshuushuuTagger(sources.BaseTagger):
    source = "e-shuushuu"
    source_domain = "e-shuushuu.net"
    resources = ["image"]

    get_resource = lambda self, url: url.path.split("/")[1][:-3]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[2]

    def check_url(self, url: str) -> bool:
        return url.startswith("https://e-shuushuu.net/image/")
