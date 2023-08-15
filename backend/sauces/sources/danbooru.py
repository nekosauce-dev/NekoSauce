import io
import typing
import urllib.parse

import grequests

import validators

from sauces import sources
from sauces.models import ArtSauce, Source, Artist, Uploader


class DanbooruFetcher(sources.BaseFetcher):
    site_name = "Danbooru"
    base_url = "https://danbooru.donmai.us"
    source = Source.objects.get(name="Danbooru")

    def get_artist_request(
        self, id: str = None, name: str = None
    ) -> grequests.AsyncRequest:
        if not id and not name:
            raise ValueError("Either id or name must be provided.")

        return (
            self.request("GET", f"/artists/{urllib.parse.quote(id)}.json")
            if id
            else self.request(
                "GET",
                f"/artists.json?search[name]={urllib.parse.quote(name)}",
            )
        )

    def _get_artist_from_response(self, artist: dict, links: list) -> Artist:
        links = list(
            set([f"https://danbooru.donmai.us/artists/{artist['id']}"] + links)
        )

        return Artist.objects.get_or_create(
            tags__overlap=[f"danbooru:artist:id:{artist['id']}"],
            defaults={
                "names": [artist["name"]] + artist["other_names"],
                "links": links,
                "tags": sources.get_tags(links)
                + [f"danbooru:artist:name:{artist['name']}"],
            },
        )[0]

    def get_artist(self, id: str = None, name: str = None) -> Artist:
        if not id and not name:
            raise ValueError("Either id or name must be provided.")

        qs = Artist.objects.filter(
            tags__overlap=[
                f"danbooru:artist:id:{id}" if id else f"danbooru:artist:name:{name}"
            ]
        )

        if qs.exists():
            return qs[0]

        rs = grequests.map(
            [
                self.get_artist_req(**({"id": id} if id else {"name": name})),
                self.request(
                    "GET",
                    f"/artist_urls.json?search[artist_id]={urllib.parse.quote(id)}"
                    if id
                    else f"/artist_urls.json?search[artist][name]={urllib.parse.quote(name)}",
                ),
            ],
            size=2,
        )
        artist = rs[0].json()
        links = list(
            set(
                [url["url"] for url in rs[1].json() if url["is_active"]]
                + [f"https://danbooru.donmai.us/artists/{id}"]
            )
        )

        if isinstance(artist, list):
            artist = artist[0]

        return self._get_artist_from_response(artist, links)

    def get_uploader_request(self, id: str) -> grequests.AsyncRequest:
        return self.request("GET", f"/users/{id}.json")

    def _get_uploader_from_response(self, uploader: dict) -> Uploader:
        return Uploader.objects.get_or_create(
            tags__overlap=[f"danbooru:user:id:{uploader['id']}"],
            defaults={
                "names": [uploader["name"]],
                "type": Uploader.Type.INDIVIDUAL,
                "links": [f"https://danbooru.donmai.us/users/{uploader['id']}"],
                "tags": sources.get_tags(
                    [f"https://danbooru.donmai.us/users/{uploader['id']}"]
                ),
            },
        )[0]

    def get_uploader(self, id: str) -> Uploader:
        qs = Uploader.objects.filter(tags__overlap=[f"danbooru:user:id:{id}"])

        if qs.exists():
            return qs[0]

        r = gevent.map(self.get_uploader_request(id))[0]

        return Uploader.objects.create(
            names=[r.json()["name"]],
            type=Uploader.Type.INDIVIDUAL,
            links=[f"https://danbooru.donmai.us/users/{id}"],
            tags=sources.get_tags([f"https://danbooru.donmai.us/users/{id}"]),
        )

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        return self.request("GET", f"/posts/{id}.json")

    def _get_sauce_from_response(
        self, post: dict, uploader: Uploader, artist: Artist
    ) -> ArtSauce:
        site_urls = (
            [f"https://danbooru.donmai.us/posts/{post['id']}"]
            + (
                [f"https://www.pixiv.net/artworks/{post['pixiv_id']}"]
                if post["pixiv_id"]
                else []
            )
            + ([post["source"]] if post["source"] else [])
        )

        sauce, created = ArtSauce.objects.get_or_create(
            tags__overlap=[f"danbooru:post:id:{post['id']}"],
            defaults={
                "title": f"Artwork from Danbooru #{post['id']} - {post['file_url'].split('/')[-1] if 'file_url' in post else 'Unknown filename'}",
                "site_urls": site_urls,
                "api_urls": [f"https://danbooru.donmai.us/posts/{post['id']}.json"],
                "file_urls": [
                    post["file_url"] if "file_url" in post else post["source"]
                ],
                "artist": artist,
                "source": self.source,
                "source_site_id": post["id"],
                "tags": sources.get_tags(site_urls),
                "height": post["image_height"],
                "width": post["image_width"],
            },
        )

        if created:
            sauce.uploaders.add(uploader)
            sauce.save()

        return sauce

    def get_sauce(self, id: str) -> ArtSauce:
        qs = ArtSauce.objects.filter(tags__overlap=[f"danbooru:post:id:{id}"])

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

    def get_sauces_list(self, page: int = 0) -> typing.List[ArtSauce]:
        response = grequests.map(
            [self.request("GET", f"/posts.json?page={page}")],
        )[0]
        sauces = response.json()

        existent_artists = Artist.objects.filter(
            tags__overlap=[
                f"danbooru:artist:name:{urllib.parse.parse_qs(sauce['tag_string_artist'])}"
                for sauce in sauces
            ]
        )
        artist_details_requests = grequests.map(
            [
                self.get_artist_request(name=sauce["tag_string_artist"].split(" ")[-1])
                for sauce in sauces
                if sauce["tag_string_artist"]
                not in set(
                    ",".join(
                        [",".join(artist.names) for artist in existent_artists]
                    ).split(",")
                )
            ],
            size=self.async_reqs,
        )
        artist_link_requests = grequests.map(
            [
                self.request(
                    "GET",
                    f"/artist_urls.json?search[artist][name]={urllib.parse.quote(sauce['tag_string_artist'])}",
                )
                for sauce in sauces
                if sauce["tag_string_artist"]
                not in set(
                    ",".join([",".join(artist.names) for artist in existent_artists])
                )
            ],
            size=self.async_reqs,
        )

        artists = {}
        for artist in artist_details_requests:
            links = []

            try:
                for links_req in artist_link_requests:
                    for link in links_req.json():
                        if (
                            link["is_active"]
                            and link["artist_id"] == artist.json()[0]["id"]
                        ):
                            links.append(link["url"])

                links = list(set(links))

                artists[artist.json()[0]["name"]] = self._get_artist_from_response(
                    artist.json()[0], links
                )
            except:
                print("WARNING: Could not create artist. {}".format(artist.url))

        for artist in existent_artists:
            artists.update({artist.names[0]: artist})

        existent_uploaders = Uploader.objects.filter(
            tags__overlap=[
                f"danbooru:user:id:{sauce['uploader_id']}" for sauce in sauces
            ]
        )
        uploader_details_requests = grequests.map(
            [
                self.get_uploader_request(sauce["uploader_id"])
                for sauce in sauces
                if f"danbooru:user:id:{sauce['uploader_id']}"
                not in set(
                    ",".join(
                        [",".join(uploader.tags) for uploader in existent_uploaders]
                    )
                )
            ],
            size=self.async_reqs,
        )

        uploaders = {}
        for uploader in uploader_details_requests:
            uploaders.update(
                {
                    uploader.json()["id"]: self._get_uploader_from_response(
                        uploader.json()
                    )
                }
            )

        return [
            self._get_sauce_from_response(
                sauce,
                uploaders[sauce["uploader_id"]],
                artists[sauce["tag_string_artist"]]
                if sauce["tag_string_artist"] and sauce["tag_string_artist"] in artists
                else None,
            )
            for sauce in sauces
            if "file_url" in sauce and sauce["file_url"]
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
    resources = ["post", "artist", "user"]

    get_resource = lambda self, url: url.path.split("/")[1][:-1]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: url.path.split("/")[2].split(".")[0]
