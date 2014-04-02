pychan
======

Python wrapper for the [new 4chan API](https://github.com/4chan/4chan-API).


Dependencies
------------

- [requests](https://github.com/kennethreitz/requests) library by kennethreitz


Installation
------------

Nothing to install. Just `git clone` the source and then `import pychan` to use
the API.


Getting Started
---------------

```python
from pychan import *
g_board = Board("g")
g_board.update_thread_index()
g_board.get_threads()            # this might take a minute
```

If we are interested in a particular thread, we can model it with a Thread
object:

```python
install_gentoo_thread = Thread("g", "39894014")     # /g/ wiki thread
install_gentoo_thread.update()
print "Sticky thread?  " + str(install_gentoo_thread.is_sticky())
print "Closed thread?  " + str(install_gentoo_thread.is_closed())
print "# of replies:   " + str(install_gentoo_thread.get_num_replies())
```

Similarly, we can track a particular page (e.g., the first page) on a board:

```python
a_front_page = Page("a", 0)
a_front_page.update()
```

We can also retrieve basic metadata about all boards:

```python
board_list = BoardList()
board_list.get_metadata()
```

We can iterate over a BoardList to play around with this metadata, like so:

```python
# print the names and titles of the worksafe boards
for board in board_list:
    if board.is_worksafe():
        print "/%s/ - %s" % (board.get_name(), board.get_title())
```
