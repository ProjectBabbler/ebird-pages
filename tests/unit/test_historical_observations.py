from datetime import time, timedelta

from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _historical_observations


class HistoricalObservationTests(TestCase):
    """
    Tests for the fields extracted for historical checklists.

    """
    def setUp(self):
        self.content = """
        <div class="report-section">
            <h5>Date and Effort</h5>
            <div class="rs-body-spp">
                <h5 class="rep-obs-date">Thu Aug 10, 2017 7:00 AM</h5>                                
            <dl class="def-list">
                <dt>Protocol:</dt>
                <dd>Historical</dd>
            </dl>
            <dl class="def-list">
                <dt>Party Size:</dt>
                <dd>1</dd>
            </dl>
            <dl class="def-list">
                <dt>Distance:</dt>
                <dd>4 kilometer(s)</dd>
            </dl>
            <dl class="def-list">
                <dt>Duration:</dt>
                <dd>4 hour(s)</dd>
            </dl>
            <dl class="def-list">
                <dt>Area:</dt>
                <dd>4 hectares</dd>
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
        return _historical_observations(tag)

    def test_fields(self):
        """Only the fields for the Traveling protocol are returned."""
        expected = ['area', 'distance', 'duration', 'observers', 'party_size', 'time']
        self.assertListEqual(expected, sorted(self.parse().keys()))

    def test_time(self):
        """The time is reported."""
        self.assertEqual(time(hour=7), self.parse()['time'])

    def test_distance(self):
        """The distance is reported."""
        self.assertEqual((4, 'km'), self.parse()['distance'])

    def test_area(self):
        """The area is reported."""
        self.assertEqual((4, 'ha'), self.parse()['area'])

    def test_duration(self):
        """The duration is reported."""
        self.assertEqual(timedelta(hours=4), self.parse()['duration'])

    def test_party_size(self):
        """The number of observers is reported."""
        self.assertEqual(1, self.parse()['party_size'])

    def test_observers(self):
        """The list of observers is reported."""
        self.assertEqual(['John Smith'], self.parse()['observers'])

    def test_time_missing(self):
        """No error is raised if the start time is missing."""
        self.content = self.content.replace('7:00 AM', '')
        self.assertFalse('time' in self.parse())

    def test_distance_missing(self):
        """No error is raised if the distance is missing."""
        self.content = self.content.replace('Distance', '')
        self.assertFalse('distance' in self.parse())

    def test_area_missing(self):
        """No error is raised if the area is missing."""
        self.content = self.content.replace('Area', '')
        self.assertFalse('area' in self.parse())

    def test_duration_missing(self):
        """No error is raised if the duration is missing."""
        self.content = self.content.replace('Duration', '')
        self.assertFalse('duration' in self.parse())

    def test_party_size_missing(self):
        """No error is raised if the number of observers is missing."""
        self.content = self.content.replace('Party Size', '')
        self.assertFalse('party_size' in self.parse())

    def test_observers_missing(self):
        """An exception is raised if the number of observers is missing."""
        self.content = self.content.replace('Observers', '')
        self.assertRaises(AttributeError, self.parse)
