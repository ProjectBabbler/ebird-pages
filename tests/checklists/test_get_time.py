from bs4 import BeautifulSoup
from datetime import time
from unittest import TestCase

from ebird.pages.checklists import _get_time


class GetDateTests(TestCase):
    """
    Tests for extracting the date and time a checklist was made.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
                <h5 class="rep-obs-date">%s</h5>
            </div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_time(tag)

    def test_time(self):
        """The time is returned as a datetime.time object."""
        self.value = 'Fri Jul 28, 2017 3:15 PM'
        expected = time(15, 15, 0, 0)
        self.assertEqual(expected, self.parse())

    def test_extra_lines(self):
        """The date can be split across several lines."""
        self.value = 'Fri \n Jul 28,\n 2017 \n3:15 PM \n'
        expected = time(15, 15, 0, 0)
        self.assertEqual(expected, self.parse())

    def test_hour_leading_zero(self):
        """The date can be extracted if the hours has a leading zero."""
        self.value = 'Fri Jul 28 2017 03:15 PM'
        expected = time(15, 15, 0, 0)
        self.assertEqual(expected, self.parse())
