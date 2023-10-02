import typing

import grequests

from nekosauce.sauces import sources
from nekosauce.sauces.utils import paginate
from nekosauce.sauces.models import Sauce


class AnimePicturesFetcher(sources.BaseFetcher):
    site_name = "Anime Pictures"
    base_url = "https://anime-pictures.net"

    def get_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request("GET", f"/api/v3/posts/{id}")

    def _get_new_sauce_from_response(self, post: dict) -> Sauce:
        return Sauce(
            site_urls=[
                f"https://anime-pictures.net/posts/{post['id']}",
            ],
            api_urls=[
                f"https://anime-pictures.net/api/v3/posts/{post['id']}",
            ],
            file_urls=[
                f"https://images.anime-pictures.net/{post['md5'][:3]}/{post['md5']}{post['ext']}",
            ],
            source_id=self.source_id,
            source_site_id=str(post["id"]),
            tags=sources.get_tags(
                [
                    f"https://anime-pictures.net/posts/{post['id']}",
                ]
            )
            + [
                f"animepictures:post:md5:{post['md5']}",
                f"animepictures:post:md5-pixels:{post['md5_pixels']}",
                f"animepictures:post:spoiler:{'yes' if post['spoiler'] else 'no'}",
                f"animepictures:post:has-alpha:{'yes' if post['have_alpha'] else 'no'}",
                f"animepictures:post:status:{post['status']}",
                f"animepictures:post:status-type:{post['status_type']}",
                f"animepictures:post:artefacts-degree:{post['artefacts_degree']}",
                f"animepictures:post:smooth-type:{post['smooth_degree']}",
                f"animepictures:post:color:{','.join([str(c) for c in post['color']])}",
            ],
            is_nsfw=post["erotics"] is not None and post["erotics"] > 0,
            height=post.get("height", 0),
            width=post.get("width", 0),
        )

    def get_sauces_iter(
        self, start_from: int = None, chunk_size: int = 1024
    ) -> typing.Iterator[Sauce]:
        last_page = grequests.map(
            [self.request("GET", "/api/v3/posts?posts_per_page=100&page=1")]
        )[0].json()["max_pages"]

        if isinstance(start_from, Sauce):
            page = (int(start_from.source_site_id) // 100) - 1
        else:
            page = last_page + 1 - int(start_from) * 100 if start_from is not None else 1

        reqs = [
            self.request(
                "GET",
                f"/api/v3/posts?posts_per_page=100&order_by=id&lang=en&page={page}",
            )
            for page in range(page, last_page)
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

                new_sauces = [
                    self._get_new_sauce_from_response(
                        post,
                    )
                    for post in response.json()["posts"]
                ]
                Sauce.objects.bulk_create(
                    new_sauces,
                    ignore_conflicts=True,
                )
                yield from new_sauces

            del req_chunks[0]

            if len(req_chunks) == 0:
                break


class AnimePicturesDownloader(sources.BaseFetcher):
    fetcher = AnimePicturesFetcher
    site_name = "Anime Pictures"

    def check_url(self, url: str) -> bool:
        return url.startswith("https://images.anime-pictures.net") or url.startswith(
            "https://cdn.anime-pictures.net"
        )

    def get_sauce_id(url: str) -> str:
        return urllib.parse.urlparse(url).path.split("/")[-1].split("?")[0]

    def download_request(self, url: str):
        return grequests.get(url)

    def download(self, url: str) -> bytes:
        r = requests.get(url)
        r.raise_for_status()

        return r.content


class AnimePicturesTagger(sources.BaseTagger):
    source = "animepictures"
    source_domain = "anime-pictures.net"
    resources = ["post"]

    get_resource = lambda self, url: url.path.split("/")[1][:-1]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[-1].split("?")[0]

    def check_url(self, url: str) -> bool:
        return url.startswith("https://anime-pictures.net/")
