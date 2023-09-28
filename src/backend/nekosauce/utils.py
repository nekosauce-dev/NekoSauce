import os
import random

import grequests
import requests


def getsecret(name: str, default=None, env_fallback: bool = True):
    """Returns a Docker secret's value.

    Args:
        name (str): The name of the secret.
        default (_type_, optional): The default value in case the secret doesn't exist. Defaults to None.
        env_fallback (bool, optional): Whether to fallback to the environment variable if the secret doesn't exist. Defaults to True.
    """

    try:
        with open("/run/secrets/" + name) as f:
            return f.read()
    except FileNotFoundError:
        return os.getenv(name, default) if env_fallback else default


class FlareSolver:
    session_id: str = "nekosauce"

    def __init__(
        self,
        flaresolver_url: str = "http://flaresolver:8191/v1",
        session_id: str = None,
    ):
        self.flaresolver_url = flaresolver_url

    def __enter__(self):
        if self.session_id is None:
            active_sessions = self.list_sessions()

            if "nekosauce" not in active_sessions:
                self.create_session("nekosauce")

            self.session_id = "nekosauce"
        return self

    def __exit__(self, exc_type = None, exc_val = None, exc_tb = None):
        self.destroy_session("nekosauce")

    def create_session(self, id: str):
        r = requests.post(
            self.flaresolver_url, json={"cmd": "session.create", "session": id}
        )
        r.raise_for_status()

        self.session_id = id

        return r.json()

    def destroy_session(self, session_id: str = None):
        r = requests.post(
            self.flaresolver_url,
            json={"cmd": "session.destroy", "session": session_id if session_id else self.session_id},
        )
        r.raise_for_status()

    def list_sessions(self):
        r = requests.post(
            self.flaresolver_url, json={"cmd": "session.list"}
        )
        r.raise_for_status()

        return r.json()["sessions"]

    def use_random_active_session(self) -> str:
        r = requests.post(self.flaresolver_url, json={"cmd": "session.list"})
        r.raise_for_status()

        sessions = r.json()["sessions"]

        if len(sessions) == 0:
            return None

        self.session_id = random.choice(sessions)

        return self.session_id

    def get(self, url: str):
        r = requests.post(
            self.flaresolver_url,
            json={"cmd": "request.get", "session": self.session_id, "url": url},
        )
        r.raise_for_status()

        return r.json()

    def aget(self, url: str) -> grequests.AsyncRequest:
        r = grequests.get(
            self.flaresolver_url,
            json={"cmd": "request.get", "session": self.session_id, "url": url},
        )
        return r
