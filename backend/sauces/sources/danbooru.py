import io
import typing
import urllib.parse

import grequests

import validators

from sauces import sources
from sauces.models import Sauce, Source, Artist, Uploader


class DanbooruFetcher(sources.BaseFetcher):
    site_name = "Danbooru"

    def get_url(self, path: str) -> str:
        return f"https://danbooru.donmai.us{path}"

    def get_artist_request(self, id: str) -> grequests.AsyncRequest:
        return grequests.get(self.get_url(f"/artists/{id}.json"))

    def get_artist(self, id: str) -> Artist:
        qs = Artist.objects.filter(tags__overlap=[f"danbooru:artist:id:{id}"])

        if qs.exists():
            return qs[0]

        rs = grequests.map(
            [
                self.get_artist_req(id),
                grequests.get(
                    self.get_url(
                        f"/artist_urls?search[artist_id]={urllib.parse.quote(id)}"
                    )
                ),
            ],
            size=2,
        )
        artist = rs[0].json()
        links = [url["url"] for url in rs[1].json() if url["is_active"]]

        return Artist.objects.create(
            names=[artist["name"]] + artist["other_names"],
            links=links + [f"https://danbooru.donmai.us/artist/{id}"],
            tags=[f"danbooru:artist:id:{id}"],
        )

    def __next__(self):
        if self.current_iter_item < len(self.loaded_iter_items):
            self.current_iter_item += 1
            return self.loaded_iter_items[self.current_iter_item - 1]
        else:
            sauces = self.list_sauces(self.current_iter_page)
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
