import os
import typing

import requests

from sources import sources


class DanbooruFetcher(sources.BaseSauceFetcher):
    def __init__(self):
        self.credentials = {
            "user": os.getenv("SAUCE_DANBOORU_USER"),
            "pass": os.getenv("SAUCE_DANBOORU_PASS"),
        }
        self.current_iter_page = 0

    def get_url(self, path: str) -> str:
        return f"https://{self.credentials['user']}:{self.credentials['pass']}@danbooru.donmai.us{path}"

    def get_poster(self, id: str) -> sources.OriginalPoster:
        r = requests.get(self.get_url(f"/posts/{id}.json"))
        r.raise_for_status()

        data = r.json()

        return sources.OriginalPoster(
            site_urls=[f"https://danbooru.donmai.us/users/{data['uploader_id']}"],
            api_urls=[f"https://danbooru.donmai.us/users/{data['uploader_id']}.json"],
            name=data["username"],
            sauce_name="Danbooru",
            sauce_site_id=data["id"],
        )

    def list_sauces(self, page: int = 0) -> typing.List[sources.Sauce]:
        return [
            sources.Sauce(
                site_urls=[
                    f"https://danbooru.donmai.us/posts/{post['id']}",
                ]
                + [f"https://www.pixiv.net/en/artworks/{post['pixiv_id']}"]
                if post["pixiv_id"] is not None
                else [],
                api_urls=[
                    f"https://danbooru.donmai.us/posts/{post['id']}.json",
                ],
                file_url=post["file_url"],
                sauce_type=sources.SauceType.ART,
                sauce_name="Danbooru",
                sauce_site_id=post["id"],
                original_poster=self.get_poster(post["uploader_id"]),
            )
            for post in requests.get(self.get_url(f"/posts.json?page={page}")).json()
        ]

    def __iter__(self):
        self.current_iter_page = 0
        return self

    def __next__(self):
        sauces = self.list_sauces(self.current_iter_page)
        self.current_iter_page = f"b{sauces[-1].sauce_site_id}"
        return sauces
