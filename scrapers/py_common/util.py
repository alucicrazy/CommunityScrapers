from functools import reduce
from typing import Any
from argparse import ArgumentParser
import sys
import json


def dig(c: dict | list, *keys: str | int | tuple, default=None) -> Any:
    """
    Helper function to get a value from a nested dict or list

    If a key is a tuple the items will be tried in order until a value is found

    :param c: dict or list to search
    :param keys: keys to search for
    :param default: default value to return if not found
    :return: value if found, None otherwise

    >>> obj = {"a": {"b": ["c", "d"], "f": {"g": "h"}}}
    >>> dig(obj, "a", "b", 1)
    'd'
    >>> dig(obj, "a", ("e", "f"), "g")
    'h'
    """

    def inner(d: dict | list, key: str | int | tuple):
        if isinstance(d, dict):
            if isinstance(key, tuple):
                for k in key:
                    if k in d:
                        return d[k]
            return d.get(key)
        elif isinstance(d, list) and isinstance(key, int) and key < len(d):
            return d[key]
        else:
            return default

    return reduce(inner, keys, c)  # type: ignore


def __create_parser(**kwargs):
    parser = ArgumentParser(argument_default=str, **kwargs)
    subparsers = parser.add_subparsers(dest="operation", required=True)

    # "Scrape with..." and the subsequent search box
    subparsers.add_parser(
        "performer-by-name", help="Search for performers"
    ).add_argument("--name", help="Performer name to search for")

    # The results of performer-by-name will be passed to this
    pbf = subparsers.add_parser("performer-by-fragment", help="Scrape a performer")
    # Technically there's more information in this fragment,
    # but in 99.9% of cases we only need the URL
    pbf.add_argument("--url", help="Scene URL")
    pbf.add_argument("--name", help="Performer name to search for")

    # Filling in an URL and hitting the "Scrape" icon
    subparsers.add_parser(
        "performer-by-url", help="Scrape a performer by their URL"
    ).add_argument("--url")

    # Filling in an URL and hitting the "Scrape" icon
    subparsers.add_parser(
        "movie-by-url", help="Scrape a movie by its URL"
    ).add_argument("--url")

    # The looking glass search icon
    # name field is guaranteed to be filled by Stash
    subparsers.add_parser("scene-by-name", help="Scrape a scene by name").add_argument(
        "--name", help="Name to search for"
    )

    # Filling in an URL and hitting the "Scrape" icon
    subparsers.add_parser(
        "scene-by-url", help="Scrape a scene by its URL"
    ).add_argument("--url")

    # "Scrape with..."
    sbf = subparsers.add_parser("scene-by-fragment", help="Scrape a scene")
    sbf.add_argument("-u", "--url")
    sbf.add_argument("--id")
    sbf.add_argument("--title")
    sbf.add_argument("--date")
    sbf.add_argument("--details")
    sbf.add_argument("--urls", nargs="+")

    # Tagger view or search box
    sbqf = subparsers.add_parser("scene-by-query-fragment", help="Scrape a scene")
    sbqf.add_argument("-u", "--url")
    sbqf.add_argument("--id")
    sbqf.add_argument("--title")
    sbqf.add_argument("--code")
    sbqf.add_argument("--details")
    sbqf.add_argument("--director")
    sbqf.add_argument("--date")
    sbqf.add_argument("--urls", nargs="+")

    # Filling in an URL and hitting the "Scrape" icon
    subparsers.add_parser(
        "gallery-by-url", help="Scrape a gallery by its URL"
    ).add_argument("--url", help="Gallery URL")

    # "Scrape with..."
    gbf = subparsers.add_parser("gallery-by-fragment", help="Scrape a gallery")
    gbf.add_argument("-u", "--url")
    gbf.add_argument("--id")
    gbf.add_argument("--title")
    gbf.add_argument("--date")
    gbf.add_argument("--details")
    gbf.add_argument("--urls", nargs="+")

    return parser


def scraper_args(**kwargs):
    """
    Helper function to parse arguments for a scraper

    This allows scrapers to be called from the command line without
    piping JSON to stdin but also from Stash

    Returns a tuple of the operation and the parsed arguments
    """
    # If stdin is not connected to a TTY the script is being executed by Stash
    called_by_stash = not sys.stdin.isatty()

    parser = __create_parser(**kwargs)
    args = vars(parser.parse_args())

    if called_by_stash:
        try:
            stash_fragment = json.load(sys.stdin)
            # print("swag", json.dumps(stash_fragment), file=sys.stderr)
            args.update(stash_fragment)
        except json.decoder.JSONDecodeError:
            # This can only happen if Stash passes invalid JSON
            sys.exit(69)

    return args.pop("operation"), args
