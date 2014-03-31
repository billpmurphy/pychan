import requests
from time import sleep

THREAD = "a.4cdn.org/%s/res/%s.json"
PAGE = "a.4cdn.org/%s/%s.json"
CATALOG_INDEX = "a.4cdn.org/%s/threads.json"
CATALOG_FULL = "a.4cdn.org/%s/catalog.json"
BOARDS = "a.4cdn.org/boards.json"

######################## Board/Thread/Post Info ########################

# coming soon

######################## Board Metadata Info ########################

class BoardMetadata():
    def __init__(self, json):
        self.title = json["title"]
        self.board = json["board"]
        self.threads_per_page = int(json["per_page"])
        self.num_pages = int(json["pages"])
        self.worksafe = True if json["ws_board"] == "1" else False
    def __str__(self):
        return self.board


class BoardList():
    def __init__(self, api = BOARDS, session = None, https = False):
        self.board_list = []
        self._api = api
        if session is None:
            self._session = requests.session()
            self._session.headers["User-Agent"] = "topkek"
        else:
            self._session = session
        self._https = https
        if self._https:
            self._url = "https://" + self._api
        else:
            self._url = "http://" + self._api
    def get_boards(self):
        res = self._session.get(self._url)
        if res.status_code == 200:
            for board_json in res.json()['boards']:
                self.board_list.append(BoardMetadata(board_json))
        else:
            res.raise_for_status()
