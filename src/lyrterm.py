#!/usr/bin/env python3
# coding=utf-8
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from os import popen
from pydoc import pager
from re import compile
from requests import get
from sys import exit

PASS_ENTRY = "api/genius"


def get_api_token() -> str:
    key = popen(f"pass show {PASS_ENTRY} | head -n 1").read().strip()
    if not key:  # handling no key in password store
        exit("Error occoured retrieving api key")
    return key


class Genius:
    def __init__(self, info: bool = False) -> None:
        self._info = info
        self.base_url = "https://api.genius.com/"
        self.headers = {"Authorization": "Bearer {}".format(get_api_token())}
        self.infos = None
        self.lyrics = None
        self.song_id = None
        self.url = None

    def get_song_id_url(self, query: str) -> None:
        request_uri = "".join([self.base_url, "search/"])
        params = {"q": query}
        response = get(request_uri, params=params, headers=self.headers).json()
        response = response["response"]["hits"][0]["result"]
        self.song_id = response["api_path"].split("/")[2]
        self.url = response["url"]

    def get_infos(self, id: str) -> None:
        request_uri = "/".join([self.base_url, "songs", id])
        params = {"song": id}
        response = get(request_uri, params=params, headers=self.headers).json()
        print(response)
        quit()

    def get_lyrics(self) -> None:
        if not self.url:
            return
        page = get(self.url).text.replace("<br/>", "\n")
        # scrape song lyrics
        page = BeautifulSoup(page, "lxml")
        # find class div
        div = page.find("div", class_=compile("^lyrics$|Lyrics__Root"))
        if div is None:
            print(f"Couldn't find the lyrics section.\nSong URL: {self.url}")
            return

        self.lyrics = div.get_text()


def parse_args():
    argparser = ArgumentParser(allow_abbrev=False)
    argparser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Print song infos along lyrics",
    )
    return argparser.parse_args()


def main() -> None:
    args = parse_args()
    query = str(input("Search for lyrics: "))
    query = query.replace(" ", "-")
    if query.lower() == "q":
        exit()
    genius = Genius(info=args.info)
    genius.get_song_id_url(query=query)
    genius.get_lyrics()
    pager(genius.lyrics)
    # genius.get_infos(id=song_id)


if __name__ == "__main__":
    main()
