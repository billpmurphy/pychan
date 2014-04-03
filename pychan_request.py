import urllib2

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


