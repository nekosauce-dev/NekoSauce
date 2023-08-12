import typing
import urllib.parse

import grequests
import requests

import validators

from sauces import sources


class DanbooruFetcher(sources.BaseSauceFetcher):
    site_name = "Danbooru"
    loaded_artists = {}

    def get_url(self, path: str) -> str:
        return f"https://danbooru.donmai.us{path}"

    def get_artists(self, tags):
        artist_reqs = [
            grequests.get(self.get_url(f"/artists.json?search[name]={urllib.parse.quote(tag)}"))
            for tag in tags
        ]
        artists = {}

        for index, response in grequests.imap_enumerated(
            artist_reqs, size=self.async_reqs
        ):
            for artist in response.json():
                if (
                    artist["name"] == tags[index]
                    or tags[index] in artist["other_names"]
                ):
                    artists[artist["id"]] = artist
                    artists[artist["id"]]["urls"] = []
                    break

        urls_reqs = [
            grequests.get(
                self.get_url(
                    f"/artist_urls.json?search[artist_id]={urllib.parse.quote(artist_id)}"
                    for artist_id in artists.keys()
                )
            )
        ]
        for response in grequests.imap(urls_reqs, size=self.async_reqs):
            for url in response.json():
                if url["artist_id"] in artists and url["is_active"] is True:
                    artists[url["artist_id"]]["urls"].append(url["url"])

        result = {}
        for artist in artists.values():
            result[artist["name"]] = sources.Artist(
                site_urls=[f"https://danbooru.donmai.us/artists/{artist['id']}"]
                + artist["urls"],
                api_urls=[f"https://danbooru.donmai.us/artists/{artist['id']}.json"],
                names=[artist["name"]] + artist["other_names"],
                sauce_name="Danbooru",
                sauce_site_id=artist["id"],
            )
        return result

    def list_sauces(
        self, page, reqs: int = 1, async_reqs: int = 5
    ) -> typing.List[sources.Sauce]:
        async_requests = []
        results = []
        page_size = 20

        if isinstance(page, str):
            first_id = int(page[1:])
            for i in range(reqs):
                async_requests.append(
                    grequests.get(
                        self.get_url(f"/posts.json?page=b{first_id - i * page_size}")
                    )
                )
        else:
            async_requests = [grequests.get(self.get_url(f"/posts.json?page={page}"))]

        for response in grequests.imap(
            async_requests, size=reqs if reqs <= async_reqs else async_reqs
        ):
            response.raise_for_status()
            posts = response.json()

            artists = self.get_artists(
                [
                    post["tag_string_artist"].split(" ")[0]
                    for post in posts
                    if post["tag_string_artist"].split(" ")[0]
                    not in self.loaded_artists
                ]
            )
            self.loaded_artists.update(artists)

            results += [
                sources.Sauce(
                    site_urls=[
                        f"https://danbooru.donmai.us/posts/{post['id']}",
                    ]
                    + ([f"https://www.pixiv.net/en/artworks/{post['pixiv_id']}"]
                    if post["pixiv_id"] is not None
                    else []),
                    api_urls=[
                        f"https://danbooru.donmai.us/posts/{post['id']}.json",
                    ],
                    file_url=post["file_url"]
                    if "file_url" in post
                    else post["source"]
                    if "source" in post
                    else None,
                    sauce_type=sources.SauceType.ART,
                    sauce_name="Danbooru",
                    sauce_site_id=post["id"],
                    artist=self.loaded_artists[post["tag_string_artist"].split(" ")[0]]
                    if post["tag_string_artist"]
                    and post["tag_string_artist"].split(" ")[0] != "banned_artist"
                    and post["tag_string_artist"].split(" ")[0] in self.loaded_artists
                    else None,
                    height=post["image_height"],
                    width=post["image_width"],
                )
                for post in posts
                if validators.url(post.get("file_url", post.get("source", None)))
            ]

        return results

    def __next__(self):
        if self.current_iter_item < len(self.loaded_iter_items):
            self.current_iter_item += 1
            return self.loaded_iter_items[self.current_iter_item - 1]
        else:
            sauces = self.list_sauces(self.current_iter_page)
            self.current_iter_page = f"b{sauces[-1].sauce_site_id}"
            self.current_iter_item = 0
            self.loaded_iter_items = sauces
            return sauces[0]
