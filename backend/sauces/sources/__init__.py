from enum import Enum
from dataclasses import dataclass

import os
import io
import typing

import grequests

from sauces.models import Sauce, Artist, Uploader


def get_fetcher(name: str):
    match name.lower():
        case "danbooru":
            from sauces.sources.danbooru import DanbooruFetcher

            return DanbooruFetcher
    return None


def get_downloader(url: str) -> Downloader:
    """Gets the downloader that will handle the given URL's download.

    Args:
        url (str): URL of the post/file to download.

    Returns:
        _type_: Downloader
    """
    from sauces.sources.danbooru import DanbooruDownloader

    downloaders = [
        DanbooruDownloader,
    ]

    for downloader in downloaders:
        if downloader.check_url(url):
            return downloader

    return None


class BaseFetcher:
    """Base class for all fetchers. Handles the fetching of sauce files from
    their sources.

    Raises:
        NotImplementedError: The requested method needs to be implemented.

    Methods:
        list_sauces(self, page: int = 0) -> typing.List[Sauce]
        get_file_url(self, url: str) -> str
        get_artist(self, id: str) -> Artist
    """

    site_name: str

    def __init__(self, iter_from=0, async_reqs=10):
        self.credentials = {
            "user": os.getenv(f"SAUCE_{self.site_name.upper()}_USER"),
            "pass": os.getenv(f"SAUCE_{self.site_name.upper()}_PASS"),
        }
        self.current_iter_page = iter_from
        self.loaded_iter_items = []
        self.current_iter_item = 0
        self.iter_from = iter_from
        self.async_reqs = async_reqs

    def get_artist_req(self, id: str) -> grequests.AsyncRequest:
        """Gets the request for the artist with the given id.

        Args:
            id (str): ID of the artist.

        Returns:
            grequests.AsyncRequest: The request (not yet executed).
        """
        raise NotImplementedError("You need to implement the `.get_artist_req()` method.")

    def get_artist(self, id: str) -> Artist:
        """Fetches the artist with the given id.

        Args:
            id (str): ID of the artist to fetch.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            sauces.models.Artist: The artist.
        """
        raise NotImplementedError("You need to implement the `.get_artist()` method.")

    def get_uploader_req(self, id: str) -> grequests.AsyncRequest:
        """Gets the request for the uploader with the given id.

        Args:
            id (str): ID of the uploader.

        Returns:
            grequests.AsyncRequest: The request (not yet executed).
        """
        raise NotImplementedError("You need to implement the `.get_uploader_req()` method.")

    def get_uploader(self, id: str) -> Uploader:
        """Fetches the uploaders from the given URL.

        Args:
            url (str): URL of the original post.

        Returns:
            sauces.models.Uploader: The post's uploader.
        """
        raise NotImplementedError(
            "You need to implement the `.get_uploaders()` method."
        )

    def get_file_url(self, url: str) -> str:
        """Fetches the file URL from the given URL.

        Args:
            url (str): URL of the original post.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            str: The file URL.
        """
        raise NotImplementedError("You need to implement the `.get_file_url()` method.")

    def list_sauces(self, page: int = 0) -> typing.List[Sauce]:
        """Fetches the list of sauces from the given page.

        Args:
            page (int, optional): The page to fetch. Defaults to 0.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            typing.List[Sauce]: The list of sauces.
        """
        raise NotImplementedError("You need to implement the `.list_sauces()` method.")

    def __iter__(self):
        self.current_iter_page = self.iter_from
        return self

    def __next__(self):
        sauces = self.list_sauces(
            self.current_iter_page, reqs=self.async_reqs, async_reqs=self.async_reqs
        )
        self.current_iter_page += 1
        return sauces


class BaseDownloader:
    """Handles the downloading of sauce files.

    Raises:
        NotImplementedError: The requested method needs to be implemented.

    Methods:
        download(self, url: str) -> io.BytesIO
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
        raise NotImplementedError("You need to implement the `.download()` method.")

    def download_request(self, url) -> grequests.AsyncRequest:
        """Returns a grequests request for the given URL. The returned request
        has not been executed yet.

        Args:
            url (str): The URL where the file is located.

        Raises:
            NotImplementedError: The requested method needs to be implemented.

        Returns:
            grequests.AsyncRequest: The request.
        """
        raise NotImplementedError(
            "You need to implement the `.download_request()` method."
        )

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
