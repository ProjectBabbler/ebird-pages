from datetime import timedelta

from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_duration


class FindDurationTests(TestCase):
    """
    Tests for finding the time spent following the checklist protocol.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>%s</dt>
                <dd>30 minute(s)</dd>
            </dl>
            </div>
        """
        self.label = None
        self.expected = timedelta(minutes=30)

    def parse(self):
        self.assertIsNotNone(self.label)
        content = self.template % self.label
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_duration(tag)

    def test_label(self):
        """The duration field can be found."""
        self.label = 'Duration:'
        self.assertEqual(self.expected, self.parse())

    def test_label_multiple_lines(self):
        """The duration label can be split over multiple lines."""
        self.label = '\n Duration: \n'
        self.assertEqual(self.expected, self.parse())

    def test_label_lower_case(self):
        """The duration label can be lower case."""
        self.label = 'duration:'
        self.assertEqual(self.expected, self.parse())

    def test_label_missing_colon(self):
        """The duration label can have the trailing colon missing."""
        self.label = 'Duration'
        self.assertEqual(self.expected, self.parse())

    def test_optional(self):
        """If the duration is cannot be found then None is returned."""
        self.label = 'Other:'
        self.expected = None
        self.assertEqual(self.expected, self.parse())


class ParseDurationTests(TestCase):
    """
    Tests for extracting the time spent following the checklist protocol.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Duration:</dt>
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
        return _get_duration(tag)

    def test_duration_hours(self):
        """The duration may be given in whole hours."""
        self.value = '1 hour(s)'
        self.assertEqual(timedelta(hours=1), self.parse())

    def test_duration_minutes(self):
        """The duration may be given in minutes."""
        self.value = '1 minute(s)'
        self.assertEqual(timedelta(minutes=1), self.parse())

    def test_duration_hours_and_minutes(self):
        """The duration may be given in hours and minutes."""
        self.value = '1 hour(s) 1 minute(s)'
        self.assertEqual(timedelta(hours=1, minutes=1), self.parse())

    def test_duration_multiple_lines(self):
        """The duration can be split over multiple lines."""
        self.value = '\n 30 \n minute(s) \n'
        self.assertEqual(timedelta(minutes=30), self.parse())
