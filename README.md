pychan
======

Pychan is an unofficial Python 2.7 wrapper for the [new 4chan API](https://github.com/4chan/4chan-API).

This repo includes:

- `pychan.py`, the main wrapper for the 4chan API
- `pychan_utils.py`, text preprocessing utilities for handling 4chan posts
- `pychan_markov.py`, a Markov model that can randomly generate 4chan comments


Getting Started
---------------

This tutorial will show you how to get started with the API, but does not go over all of its features. See the `pychan.py` source and the `help` page for a full list of all pychan objects and their methods. You can also check out the `pychan_utils.py` source for some text processing utilities, and the `pychan_markov.py` source for the Markov comment generator.


### Installation ###

Nothing to install. Just `git clone` the source and then `import pychan` to use the API.


### Tracking and Collecting Content ###

To track a board, we can create a `Board` object:

```python
from pychan import *
g_board = Board("g")
```


`Board` objects contain a list of `Page` objects, which represent each page of the board:

```python
g_board.update_pages()

# print each page number
for page in g_board:
    print "Page %s: %s threads" % (page.get_page_number(), page.get_num_threads())
```


We can track a particular page (e.g., the first page) on a board by creating our own `Page` object:

```python
a_front_page = Page("a", 0)   # first page of /a/
a_front_page.update()         # update the list of threads on the page
```


Each `Page` object contains a list of `Thread` objects, which represent the threads on that page. We can iterate over a `Page` to access its threads:

```python
# print the number of replies to the top and second-from-top /a/ threads
first_thread = a_front_page.get_threads()[0]
second_thread = a_front_page.get_threads()[1]

print "First thread has %s replies" % first_thread.get_num_replies()
print "Second thread has %s replies" % second_thread.get_num_replies()


# print the image limit from every thread on the front page of /a/
for thread in a_front_page:
    print thread.get_image_limit()
```


If we are interested in a particular thread, we can create our own `Thread` object:

```python
g_thread = Thread("g", "39894014")   # /g/ wiki thread
g_thread.update()                    # update the list of posts in the thread

print "Sticky thread?  " + str(g_thread.is_sticky())
print "Closed thread?  " + str(g_thread.is_closed())
print "# of replies:   " + str(g_thread.get_num_replies())
```


`Thread` objects are also containers of `Post` objects, which store information about individual posts. For example:

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

# is anyone using a capcode?
for post in sci_thread:
    if post.get_capcode() is not None:
        print "Yep, someone is using a capcode"
        break
```


If a post contains an image, the corresponding `Post` object will contain an `Image` object:

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
        images.append(image.download_file())
        thumbnails.append(image.download_thumbnail())
```


To recap: `Board` objects contain `Page` objects, `Page` objects contain `Thread` objects, `Thread` objects contain `Post` objects, and a `Post` object may or may not contain an `Image` object.

```python
b_board = Board("b")
b_board.update_all_threads()

# say we want to count the number of images currently available on /b/
# there are several ways of doing this:

# 1
image_sum = 0
for page in b_board:
    for thread in page:
        for post in thread:
            if post.has_image():
                image_sum += 1


# 2
image_sum = 0
for thread in b_board.get_all_threads():
    image_sum += len(thread.get_images())


# 3
image_sum = 0
for post in b_board.get_all_posts():
    if post.has_image():
        image_sum += 1


# 4 (the correct way)
image_sum = len(b_board.get_all_images())
```

### Querying Content ###

What happens when you call `Thread.update()`? Pychan uses the 4chan API to retrieve information in JSON form about a thread, and then the list of `Post` objects in the `Thread` object are destroyed and replaced with list of `Post` objects based on the JSON returned from the API query.

Similarly, when you call `Page.update()`, a new list of `Thread` objects are created based on what is returned from the API. However, note that in the case of `Page.update()`, these `Thread` objects do not contain all of the posts in the thread they represent, but instead only the OP and the most recent 3 or 4 posts. This is because calling `Page.update()` is equivalent to looking at a particular page of a particular board in a browser. If you want to retrieve all of the posts from all of the threads in the `Page`, use `Page.update_all_threads()`. This effectively calls `Page.update()` to update the list of threads on the page, and then calls `Thread.update()` on each one.

There are several ways to update the lists of pages and threads in a `Board` object:

```python
# update all pages individually
# (same as looping over the list and calling update() on each one)
# note that not all posts in a thread are collected--only the ones that would be
# visible from visiting that page, i.e. the OP and the several most recent posts
g_board.update_pages()

# update only some pages individually
# (same as looping over just these pages and calling update() on each one)
# as above, not all posts in each thread are collected
g_board.update_pages([0, 1, 2])

# update all pages using the catalog
# this updates the list of all threads on the entire board at onces, but not
# all posts from each board are collected--only the OP is retrieved
# (this is equivalent to screen-scraping the catalog page of a board)
g_board.update_from_catalog()

# update all pages at once, using the thread index
# as above, updating from the index also updates the entire board at once, but
# unlike updating from the catalog only the thread ids (not the OP text or image)
# are retrieved
g_board.update_from_index()

# update the index, then update all threads individually
# this gives you a complete snapshot of a board, i.e. all posts on all threads
# (equivalent to calling update_from_index() and then update() on each thread)
g_board.update_all_threads()
```

When any of these update methods are called, previously stored `Page`, `Thread`, and `Post` are clobbered by the new objects created from the most recent API request. This means that if you have a `Board` object and call `update_from_index()`, all of the `Thread` objects contained in that `Board` will be overwritten with new `Thread` objects. Any information about individual `Post` objects in those pre-existing `Thread` objects will not be preserved.

Again, see the `help` page or the `pychan.py` source for more details.


### Collecting Board Metadata ###

We can also retrieve basic metadata about all boards using a `BoardList`
object:

```python
board_list = BoardList()
board_list.update()        # update the list of boards
```


`BoardList` objects contain a list of `BoardMetadata` objects corresponding to each board. We can iterate over a `BoardList` to access these objects, like so:

```python
# print the names and titles of the worksafe boards
for board in board_list:
    if board.is_worksafe():
        print "/%s/ - %s" % (board.get_name(), board.get_title())
```


### Text Processing Utilities ###

The `pychan_utils.py` file contains some additional utilities for handling comments.

```python
m_board = Board("m")
m_board.update_all_threads()
comments = m_board.get_all_comments()

# preprocess and get rid of replies (e.g. >>999999), we just want the text
from pychan_utils import *
comments = map(PyChanUtils.strip_html, comments)
comments = map(PyChanUtils.exclude_replies, comments)

# grab all of the non-greentext lines from the posts
normal_text = map(PyChanUtils.exclude_greentext_lines, comments)

# what is /m/ implying today?
greentext = map(PyChanUtils.exclude_normal_lines, comments)

# I want to do text analysis, just strip out everything besides a-z letters
# and words so I can extract n-grams from the text
texts = map(PyChanUtils.full_preprocess, comments)
```

See the `pychan_utils.py` file for more details.

Markov Comment Generator
------------------------

The `pychan_markov.py` file contains a simple Markov text generator that can
output sentences that sound like comments from a particular board:

```python
from pychan_markov import *
generator = CommentGenerator("g")
generator.update_texts()              # this may take a minute or so
print generator.generate()
```

Greentext is excluded by default, but you can choose to include it in the Markov generator's corpus of sentences when you call `update_texts()`.

```python
generator = CommentGenerator("pol") # uh oh
generator.update_texts(include_greentext=True)
print generator.generate()
```


Have fun!
