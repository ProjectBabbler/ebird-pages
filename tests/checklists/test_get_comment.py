from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_comment


class FindCommentTests(TestCase):
    """
    Tests for finding the checklist comment field.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>%s</dt>
                <dd>This is a comment.</dd>
            </dl>
            </div>
        """
        self.label = None
        self.expected = 'This is a comment.'

    def parse(self):
        self.assertIsNotNone(self.label)
        content = self.template % self.label
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_comment(tag)

    def test_label(self):
        """The comment field can be found"""
        self.label = 'Comment:'
        self.assertEqual(self.expected, self.parse())

    def test_label_multiple_lines(self):
        """The comment label can be split over multiple lines."""
        self.label = '\nComment:\n'
        self.assertEqual(self.expected, self.parse())

    def test_label_lower_case(self):
        """The comment label can be lower case."""
        self.label = 'comment:'
        self.assertEqual(self.expected, self.parse())

    def test_label_missing_colon(self):
        """The comment label can have the trailing colon missing."""
        self.label = 'Comment'
        self.assertEqual(self.expected, self.parse())

    def test_comment_optional(self):
        """If the comment is missing then None is returned."""
        self.label = 'Other:'
        self.assertEqual(None, self.parse())


class GetCommentTests(TestCase):
    """
    Tests for extracting the checklist comment field.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Comment:</dt>
                <dd>%s</dd>
            </dl>
            </div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_comment(tag)

    def test_single_line(self):
        """Single line comments are extracted."""
        self.value = 'This is a comment.'
        self.assertEqual('This is a comment.', self.parse())

    def test_multiple_lines(self):
        """Comments with multiple lines are extracted."""
        self.value = 'This \n is \n a \n comment.'
        self.assertEqual('This is a comment.', self.parse())

    def test_whitespace(self):
        """Whitespace surrounding a comment in removed."""
        self.value = '\nThis is a comment.\n'
        self.assertEqual('This is a comment.', self.parse())

    def test_capitalized(self):
        """The first word in the comment is capitalized."""
        self.value = 'this is a comment.'
        self.assertEqual('This is a comment.', self.parse())
