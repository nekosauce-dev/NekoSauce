import json
import typing
import urllib.parse

import grequests
import requests


from nekosauce.utils import FlareSolverr
from nekosauce.sauces import sources
from nekosauce.sauces.utils import paginate
from nekosauce.sauces.models import Sauce, Source


def add(args):
    result = args[0]

    for arg in args[1:]:
        result += arg

    return result


class NHentaiFetcher(sources.BaseFetcher):
    site_name = "NHentai"
    source = Source.objects.get(name="NHentai")

    def __init__(self, *args, **kwargs):
        self.flaresolverr = FlareSolverr().__enter__()
        return super().__init__(*args, **kwargs)

    def get_url(self, path):
        return f"https://nhentai.net{path}"

    def request(self, path):
        return self.flaresolverr.aget(self.get_url(path))

    def get_sauce_request(self, id: str):
        doujin_id = id.split(":")[0]
        return self.request(f"/api/gallery/{doujin_id}")

    def _get_sauce_from_response(self, data, page):
        site_urls = (
            [f"https://nhentai.net/g/{data['id']}/{page}/"]
            if isinstance(page, int)
            else []
        ) + [
            f"https://nhentai.net/g/{data['id']}/",
        ]
        sauce = Sauce(
            title=f"Doujin from Nhentai #{data['id']} - {data['title']['pretty']}",
            site_urls=site_urls,
            api_urls=[
                f"https://nhentai.net/api/gallery/{data['id']}",
            ],
            file_urls=[
                f"https://i3.nhentai.net/galleries/{data['media_id']}/{page}.jpg"
                if isinstance(page, int)
                else f"https://t5.nhentai.net/galleries/{data['media_id']}/{page}.jpg"
            ],
            source=self.source,
            source_site_id=f"{data['id']}:{page}",
            tags=sources.get_tags(site_urls)
            + [
                f"nhentai:{tag['type']}:name:{urllib.parse.quote_plus(tag['name'])}"
                for tag in data["tags"]
            ]
            + [f"nhentai:{tag['type']}:id:{tag['id']}" for tag in data["tags"]]
            + (
                [f"nhentai:scanlator:name:{urllib.parse.quote_plus(data['scanlator'])}"]
                if "data['scanlator']" in data
                else []
            )
            + [
                f"nhentai:doujin:page:{page}",
                f"nhentai:doujin:media-id:{data['media_id']}",
                f"nhentai:doujin:num-pages:{data['num_pages']}",
                f"nhentai:doujin:upload-date:{data['upload_date']}",
            ]
            + [
                f"nhentai:doujin:title-{language}:{urllib.parse.quote_plus(title)}"
                for language, title in data["title"].items()
            ],
            is_nsfw=True,
            width=data["images"]["pages"][page]["width"]
            if isinstance(page, int)
            else data["images"][page]["width"],
            height=data["images"]["pages"][page]["height"]
            if isinstance(page, int)
            else data["images"][page]["height"],
        )

        return sauce

    def get_sauces_iter(
        self, chunk_size: int = 1024, start_from: int = 0
    ) -> typing.Iterator[Sauce]:
        first_page_request = self.flaresolverr.get("https://nhentai.net/api/galleries/all")
        print(first_page_request)
        first_page_data = json.loads(
            first_page_request["solution"][
                "response"
            ][131:-20]
        )

        per_page = first_page_data["per_page"]
        last_page = first_page_data["num_pages"]

        if isinstance(start_from, Sauce):
            last_page = int(start_from.source_site_id.split(":")[0]) / per_page
        elif isinstance(start_from, str):
            last_page = int(start_from.split(":")[0]) / per_page

        reqs = [
            self.request(f"/api/galleries/all?page={page}")
            for page in range(1, last_page + 1)
        ]
        reqs.reverse()

        req_chunks = paginate(reqs, chunk_size)

        while True:
            for index, response in grequests.imap_enumerated(
                req_chunks[0],
                size=self.async_reqs,
            ):
                response_json = response.json()
                if response is None or response_json["solution"]["status"] not in [
                    200,
                    "ok",
                ]:
                    return

                new_sauces = add(
                    [
                        [
                            self._get_sauce_from_response(doujin, page)
                            for page in list(range(doujin["num_pages"])) + ["cover"]
                        ]
                        for doujin in json.loads(
                            response_json["solution"]["response"][131:-20]
                        )["result"]
                    ]
                )
                Sauce.objects.bulk_create(
                    new_sauces,
                    ignore_conflicts=True,
                )
                yield from new_sauces

            del req_chunks[0]

            if len(req_chunks) == 0:
                break

        self.flaresolverr.__exit__()


class NHentaiDownloader(sources.BaseFetcher):
    fetcher = NHentaiFetcher
    site_name = "NHentai"

    def check_url(self, url: str) -> bool:
        return url.startswith("https://i3.nhentai.net") or url.startswith(
            "https://t5.nhentai.net"
        )

    def get_sauce_id(url: str) -> str:
        return urllib.parse.urlparse(url).path.split("/")[2]

    def download_request(self, url: str):
        return grequests.get(url)

    def download(self, url: str) -> bytes:
        r = requests.get(url)
        r.raise_for_status()

        return r.content


class NHentaiTagger(sources.BaseTagger):
    source = "nhentai"
    source_domain = "nhentai.net"
    resources = ["doujin"]

    get_resource = lambda self, url: "doujin"
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[2]

    def check_url(self, url: str) -> bool:
        return url.startswith("https://nhentai.net/g/")
