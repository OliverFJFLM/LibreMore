from typing import Optional

OPAC_MAP = {
    "MiyazakiSys-001": {
        "name": "宮崎市立図書館",
        "isbn_url": "https://opac.lib.miyazaki.example/search?func=search&isbn={isbn}",
    },
    "MiyazakiSys-002": {
        "name": "宮崎市 〇〇分館",
        "isbn_url": "https://opac.lib.miyazaki.example/branch2/search?isbn={isbn}",
    },
}


def opac_isbn_url(systemid: str, isbn13: str) -> Optional[str]:
    conf = OPAC_MAP.get(systemid)
    if not conf:
        return None
    return conf["isbn_url"].format(isbn=isbn13)
