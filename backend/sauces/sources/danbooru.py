import io
import typing
import urllib.parse

import requests

import validators

from sauces import sources
from sauces.models import Sauce, Source


class DanbooruFetcher(sources.BaseFetcher):
    site_name = "Danbooru"
    base_url = "https://danbooru.donmai.us"
    source = Source.objects.get(name="Danbooru")

    def get_sauce_request(self, id: str) -> requests.Response:
        return self.request("GET", f"/posts/{id}.json")

    def _get_sauce_from_response(
        self, post: dict
    ) -> Sauce:
        site_urls = (
            [f"https://danbooru.donmai.us/posts/{post['id']}"]
            + (
                [f"https://www.pixiv.net/artworks/{post['pixiv_id']}"]
                if post["pixiv_id"]
                else []
            )
            + ([post["source"]] if post["source"] else [])
        )

        sauce, created = Sauce.objects.get_or_create(
            tags__overlap=[f"danbooru:post:id:{post['id']}"],
            defaults={
                "title": f"Artwork from Danbooru #{post['id']} - {post['file_url'].split('/')[-1] if 'file_url' in post else 'Unknown filename'}",
                "site_urls": site_urls,
                "api_urls": [f"https://danbooru.donmai.us/posts/{post['id']}.json"],
                "file_urls": [
                    post["file_url"] if "file_url" in post else post["source"]
                ],
                "source": self.source,
                "source_site_id": post["id"],
                "tags": sources.get_tags(site_urls),
                "height": post["image_height"],
                "width": post["image_width"],
            },
        )

        return sauce

    def get_sauce(self, id: str) -> Sauce:
        qs = Sauce.objects.filter(tags__overlap=[f"danbooru:post:id:{id}"])

        if qs.exists():
            return qs[0]

        r = gevent.map(self.get_sauce_request(id))[0]
        post = r.json()

        return self._get_sauce_from_response(post)

    def get_file_url(self, id: str) -> str:
        qs = Source.objects.filter(tags__overlap=[f"danbooru:post:id:{id}"])

        if qs.exists():
            return qs[0].file_urls[0]

        sauce = self.get_sauce(id)
        return sauce.file_urls[0]

    def get_sauces_list(self, page: int = 0) -> typing.List[Sauce]:
        response = self.request("GET", f"/posts.json?page={page}&limit=200")
        sauces = response.json()

        return [
            self._get_sauce_from_response(
                sauce,
            )
            for sauce in sauces
            if "file_url" in sauce
            and sauce["file_url"]
            and not sauce["is_pending"]
            and not sauce["is_deleted"]
        ]

    def __next__(self):
        if self.current_iter_item < len(self.loaded_iter_items):
            self.current_iter_item += 1
            return self.loaded_iter_items[self.current_iter_item - 1]
        else:
            sauces = self.get_sauces_list(self.current_iter_page)
            self.current_iter_page = f"b{sauces[-1].source_site_id}"
            self.current_iter_item = 0
            self.loaded_iter_items = sauces
            return sauces[0]


class DanbooruDownloader(sources.BaseFetcher):
    fetcher = DanbooruFetcher

    def check_url(url: str) -> bool:
        splitted_domain = urllib.parse.urlparse(url).netloc.split(".")
        return f"{splitted_domain[-2]}.{splitted_domain[-1]}" == "donmai.us"

    def get_sauce_id(url: str) -> str:
        return urllib.parse.urlparse(url).path.split("/")[-1].split(".")[0]

    def download_request(self, url: str):
        if urllib.parse.urlparse(url).netloc == "danbooru.donmai.us":
            url = self.fetcher.get_file_url(DanbooruDownloader.get_sauce_id(url))

        return grequests.get(url)

    def download(self, url: str) -> io.BytesIO:
        if urllib.parse.urlparse(url).netloc == "danbooru.donmai.us":
            url = self.fetcher.get_file_url(DanbooruDownloader.get_sauce_id(url))

        r = requests.get(url)
        r.raise_for_status()

        return io.BytesIO(r.content)


class DanbooruTagger(sources.BaseTagger):
    source = "danbooru"
    source_domain = "danbooru.donmai.us"
    resources = ["post"]

    get_resource = lambda self, url: url.path.split("/")[1][:-1]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[2].split(".")[0]
