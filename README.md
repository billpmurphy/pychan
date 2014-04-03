pychan
======

(WORK IN PROGRESS)

Python 2.7 wrapper for the [new 4chan API](https://github.com/4chan/4chan-API).


Dependencies
------------

- Python 2.7
- [requests](https://github.com/kennethreitz/requests) library by kennethreitz


Installation
------------

Nothing to install. Just `git clone` the source and then `import pychan` to use
the API.


Getting Started
---------------

This simple tutorial will show you the basics of pychan. 

Make sure to check out the `pychan.py` source and the `help` page for a full list
of all pychan objects and their methods. 


### Tracking and Collecting Content ###

To track a board, we can create a `Board` object:

```python
from pychan import *
g_board = Board("g")
```


`Board` objects contain a list of `Page` objects, which represent each page
of the board:

```python
# print each page number
for page in g_board:
    print "Page:%s" % page.get_page_number()
```


We can track a particular page (e.g., the first page) on a board by
creating our own `Page` object:

```python
a_front_page = Page("a", 0)   # first page of /a/
a_front_page.update()         # update the list of threads on the page
```


Each `Page` object contains a list of `Thread` objects, which represent the
threads on that page. We can iterate over a `Page` to access its threads:

```python
# print the number of replies to the top and second-from-top /a/ threads
first_thread = a_front_page.get_threads()[0]
second_thread = a_front_page.get_threads()[1]

print "First thread has %s replies" % len(first_thread.get_num_replies())
print "Second thread has %s replies" % len(second_thread.get_num_replies())


# print the image limit from every thread on the front page of /a/
for thread in a_front_page:
    print thread.get_image_limit()
```


If we are interested in a particular thread, we can create our own `Thread`
object:

```python
g_thread = Thread("g", "39894014")   # /g/ wiki thread
g_thread.update()                    # update the list of posts in the thread

print "Sticky thread?  " + str(g_thread.is_sticky())
print "Closed thread?  " + str(g_thread.is_closed())
print "# of replies:   " + str(g_thread.get_num_replies())
```


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
for post in sci_thread:
    if post.has_image():
        image = post.get_image()
        print "Post ID: %s" % (post.get_number())
        print "File: %s%s" % (image.get_filename(), image.get_extension())
        print "Dimensions: %sx%s\n" % (image.get_width(), image.get_height())
```


You can also download an image or its thumbnail via the API:

```python
images = []
thumbnails = []
for post in sci_thread:
    if post.has_image():
        image = post.get_image()
        image.append(image.download_file())
        thumbnails.append(image.download_thumbnail())
```


To recap: `Board` objects contain `Page` objects, `Page` objects contain
`Thread` objects, `Thread` objects contain `Post` objects, and a `Post` object
may or may not contain an `Image` object.

```python
b_board = Board("b")
b_board.update_all_threads()

# say we want to count the number of images in /b/
# two ways of doing this:

# 1
sum = 0
for page in b_board:
    for thread in page:
        for post in thread:
            if post.has_image():
                sum += 1

# 2
sum = 0
for thread in b_board.get_all_threads():
    for post in thread:
        if post.has_image():
            sum += 1
```


Unlike `Page` and `Thread` objects, on which you can retrieve updated info just
by calling `update()`, there are actually several ways to update the list of
pages in a `Board` object: 

```python
# update all pages individually
# (same as looping over the list and calling update() on each one)
g_board.update_pages()

# update only some pages individually
# (same as looping over just these pages and calling update() on each one)
g_board.update_pages([0, 1, 2])

# update all pages using the catalog 
# (preferred, since it updates the entire board at once)
g_board.update_from_catalog()

# update all pages at once, using the thread index
# (also updates the entire board at once, but does not retrieve the OP image)
g_board.update_from_index()
```


See the `help` page or source for more details.


### Collecting Board Metadata ###

We can also retrieve basic metadata about all boards using a `BoardList`
object:

```python
board_list = BoardList()
board_list.update()        # update the list of boards
```


`BoardList` objects contain a list of `BoardMetadata` objects corresponding
to each board. We can iterate over a `BoardList` to access these objects,
like so:

```python
# print the names and titles of the worksafe boards
for board in board_list:
    if board.is_worksafe():
        print "/%s/ - %s" % (board.get_name(), board.get_title())
```
