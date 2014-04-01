import requests
from datetime import datetime
from time import sleep

THREAD = "a.4cdn.org/%s/res/%s.json"
PAGE = "a.4cdn.org/%s/%s.json"
FILE = "i.4cdn.org/%s/src/%s"
THUMBNAIL = "t.4cdn.org/%s/thumb/%ss.jpg"
CATALOG_INDEX = "a.4cdn.org/%s/threads.json"
CATALOG_FULL = "a.4cdn.org/%s/catalog.json"
BOARDS = "a.4cdn.org/boards.json"

######################## Board/Thread/Post Info ########################

class Board():
    def __init__(self, board_name, session=None, https=False):
        self.board_name = board_name
        self._https = https
        if session is None:
            self._session = requests.session()
            self._session.headers["User-Agent"] = "pychan"
        else:
            self._session = session

        self.thread_index = ThreadIndex(self.board_name, session=self._session, https=self._https)
        self.catalog = Catalog(self.board_name, session=self._session, https=self._https)
    def update_catalog(self, api = CATALOG_FULL):
        """
        Send a request and update the list of items in the Catalog object.
        """
        self.catalog.update()
    def update_thread_index(self, api=CATALOG_INDEX):
        """
        Send a request and update the list of items in the ThreadIndex object.
        """
        self.thread_index.update()
    def get_threads(self, page=None):
        """
        Retrieve all data related to the threads currently in the thread index.
        The `page` parameter selects a page to retrieve threads for, otherwise
        all threads on all pages are retrieved.
        """
        pass


class Catalog():
    def __init__(self, board_name, api=CATALOG_FULL, session=None, https=False):
        self.board_name = board_name
        self._https = https
        self._api = api % self.board_name

        if session is None:
            self._session = requests.session()
            self._session.headers["User-Agent"] = "pychan"
        else:
            self._session = session

        if self._https:
            self._url = "https://" + self._api
        else:
            self._url = "http://" + self._api
    def update(self):
        res = self._session.get(self._url)
        if res.status_code == 200:
            print res.json()
        else:
            res.raise_for_status()


class ThreadIndex():
    def __init__(self, board_name, api=CATALOG_INDEX, session=None, https=False):
        self.board_name = board_name
        self._https = https
        self._api = api % self.board_name
        self.pages = []

        if session is None:
            self._session = requests.session()
            self._session.headers["User-Agent"] = "pychan"
        else:
            self._session = session

        if self._https:
            self._url = "https://" + self._api
        else:
            self._url = "http://" + self._api
    def update(self):
        """
        Send a request and update the index of current threads.
        """
        res = self._session.get(self._url)
        if res.status_code == 200:
            if len(self.pages) == 0:
                self.pages = [list() for page in res.json()]
            for page in res.json():
                self.pages[page['page']] = \
                    [Thread.from_index(self.board_name, t) for t in page['threads']]
        else:
            res.raise_for_status()


class Page():
    def __init__(self, board, page_number):
        pass


class Thread():
    def __init__(self, board, thread_id, last_modified):
        pass
    @classmethod
    def fromJson(cls, json_data):
        """
        Create a new Thread object from a request.
        """
        pass
    @classmethod
    def from_index(cls, board_name, thread_json):
        """
        Create a new Thread object from an entry in a ThreadIndex object.
        """
        return cls(board_name, thread_json['no'], thread_json['last_modified'])
    @classmethod
    def from_catalog(cls, board_name, catalog_json):
        """
        Create a new Thread object from an entry in a Catalog object.
        """
        pass
    def update(self):
        """
        Sends a request and updates the Thread object if changes have been made
        to the thread.
        """
        pass


class Post():
    def __init__(self, thread, post_json):
        self.thread = thread
        self.has_file = post_json.has_key("filename")
        self.is_OP = post_json.get("resto", None) == 0

        self.post_number = post_json.get("no", None)
        self.poster_name = post_json.get("name", None)
        self.poster_email = post_json.get("email", None)
        self.tripcode = post_json.get("trip", None)
        self.subject = post_json.get("sub", None)
        self.comment = post_json.get("com", None)
        self.time = datetime.fromtimestamp(post_json.get("time", 0))
        self.timestamp = post_json.get("time", None)
        self.is_closed = post_json.get("closed", None) == "1"
        self.is_sticky = post_json.get("sticky", None) == "1"

        self.filename = post_json.get("filename", None)
        self.file_id = post_json.get("tim", None)
        self.file_md5_hash = post_json.get("md5", None)
        self.file_extension = post_json.get("ext", None)
        self.file_size = post_json.get("fsize", None)
        self.file_width = post_json.get("w", None)
        self.file_height = post_json.get("h", None)
        self.thumbnail_width = post_json.get("tn_w", None)
        self.thumbnail_height = post_json.get("tn_h", None)
        self.file_deleted = post_json.get("file_deleted", None) == "1"

        self.file_url = FILE % (self.thread.board.name, self.file_id + self.file_extension)
    def get_file(self):
        print self.file_url
    def get_thumbnail(self):
        pass





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
    def __init__(self, api=BOARDS, session=None, https=False):
        self.board_list = []
        self._api = api
        self._https = https

        if session is None:
            self._session = requests.session()
            self._session.headers["User-Agent"] = "pychan"
        else:
            self._session = session

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
