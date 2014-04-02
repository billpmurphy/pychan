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

######################## Board/Page/Thread/Post Info ########################

class Board():
    def __init__(self, board_name, session=None, https=False):
        self.board_name = board_name
        self._https = https
        if session is None:
            self._session = requests.session()
            self._session.headers["User-Agent"] = "pychan"
        else:
            self._session = session

        self.pages = []
        self.thread_index = ThreadIndex(self.board_name, session=self._session, https=self._https)
        self.catalog = Catalog(self.board_name, session=self._session, https=self._https)
    def __iter__(self):
        return iter(self.thread_index.pages())
    def update_catalog(self, api = CATALOG_FULL):
        """
        Send a request and update the list of items in the Catalog object.
        """
        self.catalog.update()
    def update(self, api=CATALOG_INDEX):
        """
        Send a request and update the list of items in the ThreadIndex object.
        """
        for page in self.pages:
            page.update()
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
    def __iter__(self):
        return iter(self.pages)
    def update(self):
        """
        Send a request and update the index of current threads.
        """
        res = self._session.get(self._url)
        if res.status_code == 200:
            if len(self.pages) == 0:
                self.pages = [list() for page in res.json()]
            for page in res.json():
                self.pages[page["page"]] = \
                    [Thread.from_index(self.board_name, t) for t in page["threads"]]
        else:
            res.raise_for_status()


class Page():
    def __init__(self, board_name, page_number, session=None, api=PAGE, https=False):
        self.board_name = board_name
        self.page_number = page_number
        self.threads = []
        self._https = https
        self._api = api % (self.board_name, self.page_number)

        if session is None:
            self._session = requests.session()
            self._session.headers["User-Agent"] = "pychan"
        else:
            self._session = session

        if self._https:
            self._url = "https://" + self._api
        else:
            self._url = "http://" + self._api
    def __iter__(self):
        return iter(self.threads)
    @classmethod
    def create_from_json(self, page_json):
        pass
    def update_from_json(self, page_json):
        if len(page_json.get("threads", [])) > 0:
            self.threads = [[] for i in page_json["threads"]]
            for i in range(len(self.threads)):
                self.threads[i] = Thread.create_from_json(self.board_name, \
                    page_json["threads"][i], session=self._session, https=self._https)
    def update(self):
        res = self._session.get(self._url)
        if res.status_code == 200:
            self.update_from_json(res.json())
        else:
            res.raise_from_status()


class Thread():
    def __init__(self, board_name, thread_id, session=None, api=THREAD, https=False):
        self.board_name = board_name
        self.thread_id = thread_id
        self._api = api % (self.board_name, self.thread_id)
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

        self.posts = []
        self.closed = None
        self.sticky = None
        self.bumplimit = None
        self.imagelimit = None
        self.num_replies = None
    def __iter__(self):
        return iter(self.posts)
    @classmethod
    def create_from_json(cls, board_name, json_data, session=None, api=THREAD, https=False):
        thread_id = json_data["posts"][0]["no"]
        new_thread = cls(board_name, thread_id, session=session, api=api, https=https)
        new_thread.update_from_json(json_data)
        return new_thread
    def update_from_json(self, json_data):
        """
        Updates the current Thread object from a JSON response to a thread
        API query.
        """
        OP = json_data["posts"][0]
        self.sticky = OP.get("sticky", None) == 1
        self.closed = OP.get("closed", None) == 1
        self.bumplimit = OP.get("bumplimit", None)
        self.imagelimit = OP.get("imagelimit", None)
        self.num_replies = OP.get("replies", 0)

        self.posts = [[] for i in range(len(json_data["posts"]))]
        for i in range(len(self.posts)):
            self.posts[i] = Post(self.board_name, self.thread_id, \
                json_data["posts"][i], session=self._session)
    def update(self):
        """
        Send a request and update the Thread object if changes have been made
        to the thread.
        """
        res = self._session.get(self._url)
        if res.status_code == 200:
            if len(res.json()["posts"]) > len(self.posts):
                self.update_from_json(res.json())
        else:
            res.raise_from_status()
    def is_sticky(self):
        """
        Return True if the thread is sticky, and False otherwise.
        Returns None if unknown.
        """
        return self.sticky
    def is_closed(self):
        """
        Return True if the thread is closed, and False otherwise.
        Returns None if unknown.
        """
        return self.closed
    def get_posts(self):
        """
        Returns a list of all posts in the thread, or None if they are not
        available.
        """
        return self.posts
    def get_num_replies(self):
        """
        Returns the number of replies to the OP, or None if this is not
        available.
        """
        return self.num_replies
    def get_bump_limit(self):
        """
        Returns the current bump limit, or None if this is not available.
        """
        return self.bumplimit
    def get_image_limit(self):
        """
        Returns the current image limit, or None if this is not available.
        """
        return self.imagelimit


class Post():
    def __init__(self, board_name, thread_id, post_json, session):
        self.board_name = board_name
        self.thread_id = thread_id
        self._session = session
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

        if post_json.has_key("filename"):
            self.file = Image(self.board_name, post_json, session)
        else:
            self.file = None
    def get_name(self):
        """
        Return the poster's name, if a name was entered. Otherwise return None.
        """
        return self.poster_name
    def get_email(self):
        """
        Return the poster's email, if it exists. Otherwise return None.
        """
        return self.email
    def get_number(self):
        """
        Return the post id number.
        """
        return self.post_number
    def get_tripcode(self):
        """
        Return the poster's tripcode, if it exists. Otherwise return None.
        """
        return self.tripcode
    def get_subject(self):
        """
        Return the subject field of the post.
        """
        return self.subject
    def get_comment(self):
        """
        Return the comment (i.e., the body) of the post.
        """
        return self.comment
    def get_time(self):
        """
        Return a datetime object corresponding to when the post was published.
        """
        return self.time
    def has_image(self):
        """
        Return True if the post contains an image that has not been deleted,
        otherwise return False.
        """
        if self.file is not None:
            return not self.file.is_deleted()
        return False
    def get_image(self):
        """
        Return the post's image, if it has one. Otherwise, return None.
        """
        return self.file


class Image():
    def __init__(self, board_name, post_json, session, file_api=FILE, thumb_api=THUMBNAIL):
        self.board_name = board_name
        self._session = session
        self.filename = post_json.get("filename", None)
        self.file_id = post_json.get("tim", None)
        self.file_md5_hash = post_json.get("md5", None)
        self.file_extension = post_json.get("ext", None)
        self.file_size = post_json.get("fsize", None)
        self.file_width = post_json.get("w", None)
        self.file_height = post_json.get("h", None)
        self.thumbnail_width = post_json.get("tn_w", None)
        self.thumbnail_height = post_json.get("tn_h", None)
        self.file_deleted = post_json.get("file_deleted", None) == 1

        self.file_url = file_api % (self.board_name, str(self.file_id) + self.file_extension)
        self.thumb_url = thumb_api % (self.board_name, str(self.file_id))
    def is_deleted(self):
        """
        Returns True if the file has been deleted, otherwise returns False.
        """
        return self.file_deleted
    def get_file(self):
        """
        Sends a request to retrieve the file.
        """
        if self.file_deleted:
            raise(IOError("File was deleted."))
        else:
           pass
    def get_thumbnail(self):
        """
        Sends a request to retrieve the thumbnail image.
        """
        if self.file_deleted:
            raise(IOError("File was deleted."))
        else:
            pass
    def get_filename(self):
        """
        Returns the filename of the image.
        """
        return self.filename
    def get_board_name(self):
        """
        Returns the name of the board where the file was posted, e.g. "b" or "g".
        """
        return self.board_name
    def get_file_id(self):
        """
        Returns the file id as an int.
        """
        return self.file_id
    def get_file_md5_hash(self):
        """
        Returns the MD5 hash of the file.
        """
        return self.file_md5_hash
    def get_file_size(self):
        """
        Returns the size of the file in kilobyes.
        """
        return self.file_size
    def get_extension(self):
        """
        Returns the file extension (e.g. .jpg or .png) of the file.
        """
        return self.file_extension
    def get_width(self):
        """
        Returns the width of the image.
        """
        return self.file_width
    def get_height(self):
        """
        Returns the height of image.
        """
        return self.file_height
    def get_thumbnail_width(self):
        """
        Returns the width of the jpg thumbnail.
        """
        return self.thumbnail_width
    def get_thumbnail_height(self):
        """
        Returns the height of the jpg thumbnail.
        """
        return self.thumbnail_height
    def get_file_url(self):
        """
        Returns the url for the file.
        """
        return self.file_url
    def get_thumbnail_url(self):
        """
        Returns the thumbnail url for the file.
        """
        return self.thumb_url


######################## Board Metadata Info ########################

class BoardMetadata():
    def __init__(self, json):
        self.board_title = json["title"]
        self.board_name = json["board"]
        self.threads_per_page = int(json["per_page"])
        self.num_pages = int(json["pages"])
        self.worksafe = True if json["ws_board"] == 1 else False
    def __str__(self):
        return self.board_name
    def get_name(self):
        """
        Returns the name of the board, e.g. /b/ or /g/.
        """
        return self.board_name
    def get_title(self):
        """
        Returns the title of the board, e.g. Random or Technology.
        """
        return self.board_title
    def get_num_threads_per_page(self):
        """
        Returns the number of threads per page (as an int).
        """
        return self.threads_per_page
    def get_num_pages(self):
        """
        Returns the number of pages in the board (as an int).
        """
        return self.num_pages
    def is_worksafe(self):
        """
        Returns True if the board is Safe For Work, and False otherwise.
        """
        return self.worksafe

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
    def __iter__(self):
        return iter(self.board_list)
    def get_board_list(self):
        """
        Returns the list of all boards we have metadata for.
        """
        return self.board_list
    def update(self):
        """
        Retrieves the metadata for all boards.
        """
        res = self._session.get(self._url)
        if res.status_code == 200:
            for board_json in res.json()["boards"]:
                self.board_list.append(BoardMetadata(board_json))
        else:
            res.raise_for_status()
