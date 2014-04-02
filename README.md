pychan
======

(WORK IN PROGRESS)

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

There are 7 types of objects in the API: `Board`, `Thread`, `Page`, `Post`,
`Image`, `BoardList`, and `BoardMetadata`.

To track a board, we can use a `Board` object:

```python
from pychan import *
g_board = Board("g")
```

If we are interested in a particular thread, we can model it with a Thread
object:

```python
g_thread = Thread("g", "39894014")   # /g/ wiki thread
g_thread.update()                    # update the list of posts in the thread

print "Sticky thread?  " + str(g_thread.is_sticky())
print "Closed thread?  " + str(g_thread.is_closed())
print "# of replies:   " + str(g_thread.get_num_replies())
```

Check the `help` page or the source code for the full list of methods of the
`Thread` class.

`Thread` objects are also containers of `Post` objects, which store information
about individual posts. For example:

```python
sci_thread = Thread("sci", "5942502")  # /sci/ guide thread
sci_thread.update()                    # update the list of posts in the thread

# print all of the poster names and their comments
for post in sci_thread:
    print "%s: \"%s\"" % (post.get_name(), post.get_comment())

# is anyone using a tripcode?
for post in sci_thread:
    if post.get_tripcode() is not None:
        print "Yep, someone is using a tripcode"
        break
```

If a post contains an image, the corresponding `Post` object will contain an
`Image` object:

```python
# print basic info about the images in a thread
for post in thread:
    if post.has_image():
        image = post.get_image()
        print "Post ID: %s" % (post.get_number())
        print "File: %s%s" % (image.get_filename(), image.get_extension())
        print "Dimensions: %sx%s\n" % (image.get_width(), image.get_height())
```

We can track a particular page (e.g., the first page) on a board using a
`Page` object.

```python
a_front_page = Page("a", 0)
a_front_page.update()         # update the list of threads on the page
```

Each `Page` objects contains a list of `Thread` objects, which correspond to
the threads on that page. We can iterate over a `Page` to access its threads:

```python
# print the most recent comment from every thread on the front page
for thread in a_front_page:
    print thread.get_posts()[-1].get_comment()
```

Finally, we can retrieve basic metadata about all boards using a `BoardList`
object:

```python
board_list = BoardList()
board_list.update()
```

`BoardList` objects contain a list of `BoardMetadata` objects corresponding
to each board. We can iterate over a `BoardList` to play around with these
objects, like so:

```python
# print the names and titles of the worksafe boards
for board in board_list:
    if board.is_worksafe():
        print "/%s/ - %s" % (board.get_name(), board.get_title())
```
