import urllib2
from re import sub, match
from HTMLParser import HTMLParser

######################## Text Processing Utilities ########################

class PyChanUtils():
    @staticmethod
    def strip_html(comment):
        parser = HTMLParser()
        comment = parser.unescape(comment)
        comment = sub("<w?br/?>", "\n", comment)
        comment = sub("<a href=\".+\" class=\"(\w+)\">", \
                " ", comment)
        comment = sub("</a>", " ", comment)
        comment = sub("<span class=\"(\w+)\">", " ", comment)
        comment = sub("</span>", " ", comment)
        comment = sub("<pre class=\"(\w+)\">", " ", comment)
        comment = sub("</pre>", " ", comment)
        return comment
    @staticmethod
    def exclude_replies(comment):
        lines = comment.split("\n")
        lines = filter(lambda x: not bool(match(">>(\d+)", x.strip())), lines)
        comment = "\n".join(lines)
        comment = sub(">>(\d+) ", " ", comment)
        return comment
    @staticmethod
    def exclude_greentext_lines(comment):
        lines = comment.split("\n")
        lines = filter(lambda x: not bool(match("^>([^>]+)", x.strip())), lines)
        return "\n".join(lines)
    @staticmethod
    def exclude_normal_lines(comment):
        lines = comment.split("\n")
        lines = filter(lambda x: bool(match("^[^>](.+)", x.strip())), lines)
        return "\n".join(lines)
    @staticmethod
    def full_preprocess(comment, include_greentext=True):
        comment = PyChanUtils.strip_html(comment)
        comment = PyChanUtils.exclude_replies(comment)
        if not include_greentext:
            comment = PyChanUtils.exclude_greentext_lines(comment)

        comment = sub("[^\x00-\x7F]", " ", comment)
        comment = comment.lower()
        comment = sub("&(amp|lt|gt|ge|le)(;|)", " ", comment)
        comment = sub("http([^ ]*)", " ", comment)

        # make sure words are joined on m-dashes and quotes,
        # e.g. don't -> dont
        comment = sub("[^a-z \-']+", " ", comment)
        comment = sub("'|-", "", comment)

        comment = sub("\\s\\s+", " ", comment)
        comment = sub("\n", " ", comment)
        comment = str(comment).strip()
        return comment


######################## HTTP Request Utilities ########################

class PyChanRequest():
    @staticmethod
    def get(url, user_agent="pychan"):
        """
        Naive URL handler; retrieves a resource from a URL.
        """
        request = urllib2.Request(url)
        request.add_header("User-Agent", user_agent)
        response = urllib2.urlopen(request)

        if response.code == 200:
            data = response.read()
            response.close()
            return data
        else:
            raise(urllib2.URLError("Status: %s" % response.code))


