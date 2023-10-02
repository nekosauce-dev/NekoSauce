import typing
import urllib.parse

import grequests
import requests

from nekosauce.sauces import sources
from nekosauce.sauces.utils import paginate
from nekosauce.sauces.models import Sauce


class YandereFetcher(sources.BaseFetcher):
    site_name = "Yande.re"

    def get_url(self, path: str) -> str:
        return f"https://yande.re{path}"

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request("GET", f"/posts/{id}.json")

    def get_file_url(self, id: str) -> str:
        qs = Sauce.objects.filter(tags__overlap=[f"yandere:post:id:{id}"])

        if qs.exists():
            return qs[0].file_urls[0]

        sauce = self.get_sauce(id)
        return sauce.file_urls[0]

    def _get_new_sauce_from_response(self, post: dict) -> Sauce:
        site_urls = [
            f"https://yande.re/post/show/{post['id']}",
        ] + ([post["source"]] if post["source"] else [])

        sauce = Sauce(
            site_urls=site_urls,
            api_urls=[
                f"https://yande.re/post.json?tags=id:{post['id']}",
            ],
            file_urls=[post["file_url"]],
            source_id=self.source_id,
            source_site_id=str(post["id"]),
            tags=sources.get_tags(site_urls)
            + [
                f"yandere:post:md5:{post['md5']}",
                f"yandere:post:rating:{post['rating']}",
            ]
            + [f"yandere:tag:name:{tag}" for tag in post["tags"].split(" ")]
            + (
                [f"yandere:author:name:{urllib.parse.quote_plus(post['author'])}"]
                if post["author"]
                else []
            ),
            is_nsfw=post["rating"] in ["q", "e"],
            width=post["width"] if post["width"] is not None else 0,
            height=post["height"] if post["height"] is not None else 0,
        )

        return sauce

    def get_sauce(self, id: str) -> Sauce:
        qs = Sauce.objects.filter(tags__overlap=[f"yandere:post:id:{id}"])

        if qs.exists():
            return qs[0]

        r = grequests.map(self.get_sauce_request(id))[0]
        post = r.json()

        return self._get_sauce_from_response(post)

    def get_sauces_iter(
        self, chunk_size: int = 1024, start_from=None
    ) -> typing.Iterator[Sauce]:
        last_yandere_sauce_id = int(
            requests.get(self.get_url("/post.json?limit=1")).json()[0]["id"]
        )

        if isinstance(start_from, Sauce):
            start_from = int(start_from.source_site_id)
        else:
            start_from = int(start_from) if start_from is not None else 0

        page_range = 100

        reqs = [
            self.request(
                "GET",
                f"/post.json?limit={page_range}&tags=id:{','.join([str(n) for n in range(i, i + page_range)])}",
            )
            for i in range(start_from, last_yandere_sauce_id + 1, page_range)
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

                if response.status_code == 520:
                    continue

                new_sauces = [
                    self._get_new_sauce_from_response(
                        post,
                    )
                    for post in response.json()
                    if (
                        "file_url" in post
                        and post["file_url"]
                        and post["status"] == "active"
                    )
                ]
                Sauce.objects.bulk_create(
                    new_sauces,
                    ignore_conflicts=True,
                )
                yield from new_sauces

                for sauce in new_sauces:
                    if sauce.source_site_id == str(last_yandere_sauce_id):
                        return

            del req_chunks[0]

            if len(req_chunks) == 0:
                break


class YandereDownloader(sources.BaseDownloader):
    fetcher = YandereFetcher
    site_name = "Yande.re"

    def check_url(self, url: str) -> bool:
        return url.startswith("https://files.yande.re")

    def get_sauce_id(url: str) -> str:
        return urllib.parse.urlparse(url).path.split("/")[-1].split(".")[0]

    def download_request(self, url: str):
        if urllib.parse.urlparse(url).path.startswith("/post/"):
            url = self.fetcher.get_file_url(YandereDownloader.get_sauce_id(url))

        return grequests.get(url)

    def download(self, url: str) -> bytes:
        if urllib.parse.urlparse(url).path.startswith("/post/"):
            url = self.fetcher().get_file_url(YandereDownloader.get_sauce_id(url))

        r = requests.get(url)
        r.raise_for_status()

        return r.content


class YandereTagger(sources.BaseTagger):
    source = "yandere"
    source_domain = "yande.re"
    resources = ["post"]

    get_resource = lambda self, url: url.path.split("/")[1]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[-1].split(".")[0]

    def check_url(self, url: str) -> bool:
        return url.startswith("https://yande.re")

    def to_url(self, tag) -> str:
        """Converts a tag into a URL.

        Args:
            tag (str): The tag to be converted.

        Raises:
            NotImplementedError: The requested algorithm needs to be implemented.
            ValueError: The tag is invalid.

        Returns:
            str: The URL.
        """
        source, resource, prop, value = tuple(tag.split(":", 3))
        return f"https://{self.source_domain}/{resource}/show/{value}"
