from pychan import *
from pychan_utils import *
from random import choice
from HTMLParser import HTMLParser

class CommentGenerator():
    """
    A Markov model to generate something that looks like a 4chan comment using
    text extracted from a 4chan board.
    """
    def __init__(self, board_name):
        self.board = Board(board_name)
        self.texts = []
        self.start_words = []
        self.word_pairs = {}
    def update_texts(self, include_greentext=False, plaintext=False):
        """
        Query the API for all threads in the board and update the Markov model
        using all of the comments from these threads, excluding greentext.
        """
        self.board.update_all_threads()

        comments = self.board.get_all_comments()
        if plaintext:
            for text in comments:
                text = PyChanUtils.full_preprocess(text, include_greentext)
                self.texts.append(text)
        else:
            for text in comments:
                text = PyChanUtils.strip_html(text)
                text = PyChanUtils.exclude_replies(text)
                if not include_greentext:
                    PyChanUtils.exclude_greentext_lines(text)
                self.texts.append(text)

        for text in self.texts:
            tokens = text.split(" ")
            tokens = filter(lambda x: x != "", tokens)

            if len(tokens) > 0:
                self.start_words.append(tokens[0])

                for i in range(len(tokens)-1):
                    if self.word_pairs.has_key(tokens[i]):
                        self.word_pairs[tokens[i]].append(tokens[i+1])
                    else:
                        self.word_pairs[tokens[i]] = [tokens[i+1]]

                if self.word_pairs.has_key(tokens[-1]):
                    self.word_pairs[tokens[-1]].append(None)
                else:
                    self.word_pairs[tokens[-1]] = [None]
    def generate(self):
        """
        Use a Markov process to generate a new comment.
        """
        key = choice(self.start_words)
        comment = key
        next_word = choice(self.word_pairs[key])
        while next_word is not None:
            comment += " " + next_word
            key = next_word
            next_word = choice(self.word_pairs[key])
        return comment
    def get_texts(self):
        """
        Return the corpus of texts the generator is using.
        """
        return self.texts

