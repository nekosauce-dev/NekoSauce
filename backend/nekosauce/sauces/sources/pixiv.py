import re

from nekosauce.sauces import sources


class PixivTagger(sources.BaseTagger):
    source = "pixiv"
    source_domain = "www.pixiv.net"
    resources = ["artwork", "user"]

    get_resource = lambda self, url: re.match(self.path_pattern, url.path)[-2]
    get_property = lambda self, url: "id"
    get_value = lambda self, url: re.match(self.path_pattern, url.path)[-1]

    path_pattern = (
        r"^(/[a-zA-Z]+)?/(?P<resource_name>artworks|users)/(?P<resource_id>[0-9]+)"
    )

    def check_url(self, url: str) -> bool:
        try:
            parsed_url = urllib.parse.urlparse(url)
            splitted_domain = parsed_url.netloc.split(".")
            return (
                f"{splitted_domain[-2]}.{splitted_domain[-1]}" == "pixiv.net"
                and re.match(self.path_pattern, parsed_url.path) is not None
            )
        except Exception as e:
            return False
