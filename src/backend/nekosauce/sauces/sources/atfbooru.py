import io
import typing
import urllib.parse

from django.db.models import Q

import grequests
import requests

import validators

from nekosauce.sauces import sources
from nekosauce.sauces.utils import paginate
from nekosauce.sauces.models import Sauce, Source


class ATFBooruFetcher(sources.BaseFetcher):
    site_name = "ATFBooru"
    source = Source.objects.get(name="ATFBooru")

    last_page = property(lambda self: f"a{self.last_sauce.source_site_id}")

    def get_url(self, path: str) -> str:
        return f"https://booru.allthefallen.moe{path}"

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request("GET", f"/posts/{id}.json")

    def _get_new_sauce_from_response(self, post: dict) -> Sauce:
        site_urls = (
            [f"https://booru.allthefallen.moe/posts/{post['id']}"]
            + (
                [f"https://www.pixiv.net/artworks/{post['pixiv_id']}"]
                if post["pixiv_id"]
                else []
            )
            + ([post["source"]] if post["source"] else [])
        )

        sauce = Sauce(
            title=f"Artwork from ATFBooru #{post['id']} - {post['file_url'].split('/')[-1] if 'file_url' in post else 'Unknown filename'}",
            site_urls=site_urls,
            api_urls=[f"https://booru.allthefallen.moe/posts/{post['id']}.json"],
            file_urls=[post.get("file_url", post["source"])],
            source=self.source,
            source_site_id=post["id"],
            tags=sources.get_tags(
                site_urls
                + ([post.get("source")] if validators.url(post.get("source")) else [])
                + (
                    [f"https://www.pixiv.net/artworks/{post.get('pixiv_id')}"]
                    if post.get("pixiv_id")
                    else []
                )
            )
            + (
                [
                    f"atfbooru:artist:name:{urllib.parse.quote_plus(post['tag_string_artist'])}"
                ]
                if "tag_string_artist" in post and post["tag_string_artist"]
                else []
            )
            + (
                [
                    f"atfbooru:tag:name:{urllib.parse.quote_plus(tag)}"
                    for tag in post["tag_string_general"].split(" ")
                    if tag
                ]
                if "tag_string_general" in post and post["tag_string_general"]
                else []
            )
            + (
                [
                    f"atfbooru:character:name:{urllib.parse.quote_plus(tag)}"
                    for tag in post["tag_string_character"].split(" ")
                    if tag
                ]
                if "tag_string_character" in post and post["tag_string_character"]
                else []
            )
            + (
                [
                    f"atfbooru:copyright:name:{urllib.parse.quote_plus(tag)}"
                    for tag in post["tag_string_copyright"].split(" ")
                    if tag
                ]
                if "tag_string_copyright" in post and post["tag_string_copyright"]
                else []
            )
            + (
                [
                    f"atfbooru:meta-tag:name:{urllib.parse.quote_plus(tag)}"
                    for tag in post["tag_string_meta"].split(" ")
                    if tag
                ]
                if "tag_string_meta" in post and post["tag_string_meta"]
                else []
            ),
            is_nsfw=post["rating"] in ["q", "e"],
            height=post["image_height"],
            width=post["image_width"],
        )

        return sauce

    def get_sauce(self, id: str) -> Sauce:
        qs = Sauce.objects.filter(tags__overlap=[f"atfbooru:post:id:{id}"])

        if qs.exists():
            return qs[0]

        r = grequests.map(self.get_sauce_request(id))[0]
        post = r.json()

        return self._get_sauce_from_response(post)

    def get_file_url(self, id: str) -> str:
        qs = Source.objects.filter(tags__overlap=[f"atfbooru:post:id:{id}"])

        if qs.exists():
            return qs[0].file_urls[0]

        sauce = self.get_sauce(id)
        return sauce.file_urls[0]

    def get_sauces_iter(self, chunk_size: int = 1024, start_from = None) -> typing.Iterator[Sauce]:
        greatest_id = requests.get("https://booru.allthefallen.moe/posts.json").json()[0]["id"]

        if start_from is not None and (
            isinstance(start_from, Sauce) or not start_from.isnumeric()
        ):
            page = ( 
                 f"a{start_from.source_site_id}" 
                 if isinstance(start_from, Sauce) 
                 else start_from 
             ) 
             ids = list(range(int(page[1:]) - 200, (greatest_id // 200) + 1, 200)) 
             reqs = [ 
                 self.request( 
                     "GET", 
                     "/posts.json?page=a{page}&limit=200".format(page=i), 
                 ) 
                 for i in ids 
             ]        else:
            page = int(start_from) if start_from is not None else 1
            reqs = [
                self.request(
                    "GET",
                    "/posts.json?page=a{page}&limit=200".format(page=i),
                )
                for i in range(page, page + 1000000, 200)
            ]

        req_chunks = paginate(reqs, chunk_size)

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
                    for post in response.json()
                    if (
                        "file_url" in post
                        and post["file_url"]
                        and not post["is_pending"]
                        and not post["is_deleted"]
                    )
                ]
                Sauce.objects.bulk_create(
                    new_sauces,
                    ignore_conflicts=True,
                )
                yield from new_sauces

                for sauce in new_sauces:
                    if sauce.source_site_id == str(greatest_id):
                        return
            
            del req_chunks[0]

            if len(req_chunks) == 0:
                break


class ATFBooruDownloader(sources.BaseFetcher):
    fetcher = ATFBooruFetcher
    site_name = "ATFBooru"

    def check_url(self, url: str) -> bool:
        return url.startswith("https://booru.allthefallen.moe")

    def get_sauce_id(url: str) -> str:
        return urllib.parse.urlparse(url).path.split("/")[-1].split(".")[0]

    def download_request(self, url: str):
        if urllib.parse.urlparse(url).netloc == "booru.allthefallen.moe":
            url = self.fetcher.get_file_url(ATFBooruDownloader.get_sauce_id(url))

        return grequests.get(url)

    def download(self, url: str) -> bytes:
        if urllib.parse.urlparse(url).netloc == "booru.allthefallen.moe":
            url = self.fetcher.get_file_url(ATFBooruDownloader.get_sauce_id(url))

        r = requests.get(url)
        r.raise_for_status()

        return r.content


class ATFBooruTagger(sources.BaseTagger):
    source = "atfbooru"
    source_domain = "booru.allthefallen.moe"
    resources = ["post"]

    get_resource = lambda self, url: url.path.split("/")[1][:-1]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[2].split(".")[0]

    def check_url(self, url: str) -> bool:
        return url.startswith("https://booru.allthefallen.moe/")
