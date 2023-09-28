from enum import Enum
from dataclasses import dataclass

import os
import io
import typing
import urllib.parse

import grequests
import requests

from nekosauce.sauces.models import Sauce, Source


def get_all_fetchers():
    from nekosauce.sauces.sources.lolibooru import LolibooruFetcher
    from nekosauce.sauces.sources.danbooru import DanbooruFetcher
    from nekosauce.sauces.sources.gelbooru import GelbooruFetcher
    from nekosauce.sauces.sources.konachan import KonachanFetcher
    from nekosauce.sauces.sources.atfbooru import ATFBooruFetcher
    from nekosauce.sauces.sources.yandere import YandereFetcher
    from nekosauce.sauces.sources.aibooru import AIBooruFetcher
    from nekosauce.sauces.sources.rule34 import Rule34Fetcher

    return [
        LolibooruFetcher,
        GelbooruFetcher,
        DanbooruFetcher,
        KonachanFetcher,
        ATFBooruFetcher,
        YandereFetcher,
        AIBooruFetcher,
        Rule34Fetcher,
    ]


def get_fetcher(name: str) -> "BaseFetcher":
    fetchers = get_all_fetchers()

    for fetcher in fetchers:
        if fetcher.site_name.lower() == name.lower():
            return fetcher

    return None


def get_downloader(url: str) -> "BaseDownloader":
    """Gets the downloader that will handle the given URL's download.

    Args:
        url (str): URL of the post/file to download.

    Returns:
        _type_: Downloader
    """
    from nekosauce.sauces.sources.lolibooru import LolibooruDownloader
    from nekosauce.sauces.sources.danbooru import DanbooruDownloader
    from nekosauce.sauces.sources.gelbooru import GelbooruDownloader
    from nekosauce.sauces.sources.konachan import KonachanDownloader
    from nekosauce.sauces.sources.atfbooru import ATFBooruDownloader
    from nekosauce.sauces.sources.yandere import YandereDownloader
    from nekosauce.sauces.sources.aibooru import AIBooruDownloader
    from nekosauce.sauces.sources.rule34 import Rule34Downloader

    downloaders = [
        LolibooruDownloader,
        DanbooruDownloader,
        GelbooruDownloader,
        KonachanDownloader,
        ATFBooruDownloader,
        YandereDownloader,
        AIBooruDownloader,
        Rule34Downloader,
    ]

    for downloader in downloaders:
        if downloader().check_url(url):
            return downloader

    return None


def get_tags(links: typing.List[str]) -> typing.List[str]:
    """Gets the tags for the given list of links.

    Args:
        links (typing.List[str]): List of links.

    Returns:
        typing.List[str]: List of tags.
    """
    from nekosauce.sauces.sources.lolibooru import LolibooruTagger
    from nekosauce.sauces.sources.danbooru import DanbooruTagger
    from nekosauce.sauces.sources.gelbooru import GelbooruTagger
    from nekosauce.sauces.sources.konachan import KonachanTagger
    from nekosauce.sauces.sources.atfbooru import ATFBooruTagger
    from nekosauce.sauces.sources.yandere import YandereTagger
    from nekosauce.sauces.sources.aibooru import AIBooruTagger
    from nekosauce.sauces.sources.rule34 import Rule34Tagger
    from nekosauce.sauces.sources.pixiv import PixivTagger

    taggers = [
        LolibooruTagger(),
        DanbooruTagger(),
        GelbooruTagger(),
        KonachanTagger(),
        ATFBooruTagger(),
        YandereTagger(),
        AIBooruTagger(),
        Rule34Tagger(),
        PixivTagger(),
    ]

    result = []

    for link in links:
        for tagger in taggers:
            if tagger.check_url(link):
                try:
                    result.append(tagger.to_tag(link))
                    break
                except ValueError:
                    pass

    return result


def _not_implemented_error(msg: str):
    raise NotImplementedError(msg)


class BaseFetcher:
    """Base class for all fetchers. Handles the fetching of sauce files from
    their sources.

    Raises:
        NotImplementedError: The requested algorithm needs to be implemented.

    Methods:
        get_url(path): Returns the URL for the given path.
        request(algorithm, url, **kwargs): Makes a request to the Sauce API.
        get_artist_request(id): Gets the request for the artist with the given id.
        get_artist(id): Gets the artist with the given id.
        get_uploader_request(id): Gets the request for the uploader with the given id.
        get_uploader(id): Gets the uploader with the given id.
        get_file_url(url): Gets the URL for the given file.
        get_sauces_list(page): Gets the list of sauces for the given page.
    """

    site_name: str = None
    base_url: str = None
    source: Source = None

    def __init__(self, async_reqs: int = 10):
        self.credentials = {
            "user": os.getenv(f"BACKEND_SOURCE_{self.site_name.upper()}_USERNAME"),
            "pass": os.getenv(f"BACKEND_SOURCE_{self.site_name.upper()}_PASSWORD"),
        }
        self.async_reqs = async_reqs

    @property
    def last_sauce(self) -> Sauce:
        return Sauce.objects.filter(source=self.source).order_by("-created_at").first()

    @property
    def last_page(self) -> int:
        raise NotImplementedError(
            "You need to implement the `.last_page()` property algorithm."
        )

    def get_url(self, path: str) -> str:
        """Returns the URL for the given path.

        Args:
            path (str): Path of the file to download.

        Returns:
            str: The URL
        """
        if self.base_url:
            return f"{self.base_url}{path}"

        raise NotImplementedError(
            "You need to implement either the `get_url()` method or set the `base_url` attribute."
        )

    def request(self, method, url, **kwargs) -> grequests.AsyncRequest:
        """Makes a request to the Sauce API.

        Args:
            method (str): HTTP method.
            url (str): URL of the post/file to download.

        Returns:
            grequests.AsyncRequest: The request's response.
        """
        return grequests.request(method, self.get_url(url), **kwargs)

    def get_file_url(self, id: str) -> str:
        """Fetches the file URL from the given URL.

        Args:
            id (str): ID of the original post's file.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            str: The file URL.
        """
        raise NotImplementedError("You need to implement the `.get_file_url()` method.")

    def get_sauce_request(self, id: str) -> grequests.AsyncRequest:
        """Gets the request for the sauce with the given id.

        Args:
            id (str): ID of the sauce.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            grequests.AsyncRequest: The request (not yet executed).
        """
        raise NotImplementedError(
            "You need to implement the `.get_sauce_request()` method."
        )

    def get_sauces_iter(self, start_from: int = 0) -> typing.Iterator[Sauce]:
        """Fetches all sauces possible, starting from the given page.

        Args:
            start_from (int, optional): The page to start from. Defaults to 0.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            typing.Iterator[Sauce]: The iterator.
        """
        raise NotImplementedError("You need to implement the `.get_iter()` method.")


class BaseDownloader:
    """Handles the downloading of sauce files.

    Raises:
        NotImplementedError: The requested method needs to be implemented.

    Methods:
        download(self, url: str) -> io.BytesIO
        download_request(self, url: str) -> grequests.AsyncRequest
        check_url(self, url: str) -> bool
        get_sauce_id(self, url: str) -> str
    """

    fetcher: BaseFetcher

    def download(self, url) -> io.BytesIO:
        """Downloads the sauce file from the given URL.

        Args:
            url (str): The URL where the file is located.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            io.BytesIO: The downloaded file.
        """
        r = grequests.map(self.download_request(url))[0]
        r.raise_for_status()

        return io.BytesIO(r.content)

    def download_request(self, url) -> grequests.AsyncRequest:
        """Returns a grequests.AsyncRequest for the given URL. The returned request
        has not been executed yet.

        Args:
            url (str): The URL where the file is located.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            grequests.AsyncRequest: The request.
        """
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=10)
        session.mount("http://", adapter)

        return grequests.get(self.fetcher.get_url(url), session=session)

    def check_url(self, url) -> bool:
        """Checks if a URL can be downloaded by this downloader.

        Args:
            url (str): The URL to be checked.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            bool: Wether this downloader can handle this URL download or not.
        """
        raise NotImplementedError("You need to implement the `.check_url()` method.")

    def get_sauce_id(self, url) -> str:
        """Returns the post ID from a Danbooru post URL.

        Args:
            url (str): The URL of the post.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            str: The post ID.
        """
        raise NotImplementedError("You need to implement the `.get_sauce_id()` method.")


class BaseTagger:
    """Converts URLs into tags and vice versa. Tags follow the
    {source}:{resource}:{property}:{prop-value} format.

    Methods:
        check_resources(self, resource) -> bool
        check_url(self, url) -> bool
        to_tag(self, url) -> str
        to_url(self, tag) -> str
    """

    source: str
    source_domain: str
    resources: typing.List[str]

    get_source: typing.Callable = lambda self, parsed_url: self.source
    get_resource: typing.Callable = lambda self, parsed_url: _not_implemented_error(
        "The `get_resource()` method is not implemented."
    )
    get_property: typing.Callable = lambda self, parsed_url: _not_implemented_error(
        "The `get_property()` method is not implemented."
    )
    get_value: typing.Callable = lambda self, parsed_url: _not_implemented_error(
        "The `get_value()` method is not implemented."
    )

    def check_resources(self, resource, raise_error: bool = True):
        """Checks if a resource can be converted into a tag.

        Args:
            resource (str): The resource to be checked.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            bool: Wether this tagger can handle this resource or not.
        """
        if resource not in self.resources and raise_error:
            raise ValueError(
                "The URL is invalid. The resource must be one of "
                + ", ".join([f"`{resource}`" for resource in self.resources])
                + f", but instead it's `{resource}`"
            )

        return resource in self.resources

    def check_url(self, url) -> bool:
        """Checks if a URL can be converted into a tag.

        Args:
            url (str): The URL to be checked.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            bool: Wether this tagger can handle this URL or not.
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            return parsed_url.netloc == self.source_domain
        except ValueError:
            return False

    def to_tag(self, url) -> str:
        """Converts a URL into a tag.

        Args:
            url (str): The URL to be converted.

        Raises:
            NotImplementedError: The requested method needs to be implemented.
            ValueError: The URL is invalid.

        Returns:
            str: The tag.
        """
        parsed_url = urllib.parse.urlparse(url)

        source = self.get_source(parsed_url)
        resource = self.get_resource(parsed_url)
        prop = self.get_property(parsed_url)
        value = self.get_value(parsed_url)

        self.check_resources(resource)

        return f"{source}:{resource}:{prop}:{value}"

    def to_url(self, tag) -> str:
        """Converts a tag into a URL.

        Args:
            tag (str): The tag to be converted.

        Raises:
            NotImplementedError: The requested method needs to be implemented.
            ValueError: The tag is invalid.

        Returns:
            str: The URL.
        """
        source, resource, prop, value = tuple(tag.split(":", 3))
        return f"https://{self.source_domain}/{resource}s/{value}"
