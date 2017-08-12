from datetime import time, timedelta

from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _incidental_observations


class IncidentalProtocolTests(TestCase):
    """
    Tests for the fields extracted for checklists with incidental
    observations.

    """
    def setUp(self):
        self.content = """
        <div class="report-section">
            <h5>Date and Effort</h5>
            <div class="rs-body-spp">
                <h5 class="rep-obs-date">Thu Aug 10, 2017 7:00 AM</h5>                                
            <dl class="def-list">
                <dt>Protocol:</dt>
                <dd>Incidental</dd>
            </dl>
            <dl class="def-list">
                <dt>Observers:</dt>
                <dd><strong>John Smith</strong></dd>
            </dl>
            <dl class="def-list report-comments">
                <dt>Comments:</dt>
                <dd></dd>
            </dl>
        </div>
        """

    def parse(self):
        soup = BeautifulSoup(self.content, "lxml")
        tag = soup.find('div', class_='report-section')
        return _incidental_observations(tag)

    def test_fields(self):
        """Only the fields for the Traveling protocol are returned."""
        expected = ['observers', 'time']
        self.assertListEqual(expected, sorted(self.parse().keys()))

    def test_time(self):
        """The time is reported."""
        self.assertEqual(time(hour=7), self.parse()['time'])

    def test_observers(self):
        """The list of observers is reported."""
        self.assertEqual(['John Smith'], self.parse()['observers'])

    def test_time_missing(self):
        """No error is raised if the start time is missing."""
        self.content = self.content.replace('7:00 AM', '')
        self.assertFalse('time' in self.parse())

    def test_observers_missing(self):
        """An exception is raised if the number of observers is missing."""
        self.content = self.content.replace('Observers', '')
        self.assertRaises(AttributeError, self.parse)
