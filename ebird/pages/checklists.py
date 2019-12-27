# TODO Add support for entry comments.
# TODO Add support for age/sex breakdown
# TODO Add support for extracting information on uploaded media.
# TODO Add support for Oiled Birds protocol

import datetime
import re

from bs4 import BeautifulSoup

from ebird.pages.utils import get_content

# Base URL for the page to view a checklist - the unique identifier is
# appended.

CHECKLIST_URL = "https://ebird.org/checklist/"

# The list of supported protocols.

PROTOCOLS = (
    'Stationary',
    'Traveling',
    'Incidental',
    'Historical',
    'Area,',
    'Banding',
    'eBird Pelagic Protocol',
    'Nocturnal Flight Call Count',
    'Random',
    'CWC Point Count',
    'CWC Area Count',
    'PROALAS',
    'TNC California Waterbird Count',
    'Rusty BlackbirdSpring Migration Blitz',
    'California Brown Pelican Survey',
)


def get_checklist(identifier):
    """
    Get the data for a checklist from its eBird web page.

    :param identifier: the unique identifier for the checklist.

    :return: a dict containing all the fields extracted from the web page.

    """
    checklist = {}

    content = get_content(CHECKLIST_URL + identifier)
    parser = BeautifulSoup(content, "lxml")

    sections = parser.find_all('div', class_='report-section')

    checklist['identifier'] = identifier
    checklist['location'] = _get_location(sections[0])
    checklist.update(_get_date_and_effort(sections[1]))
    checklist['entries'] = _get_entries(sections[2])
    checklist['complete'] = _get_complete(sections[3])

    return checklist


def _get_location(node):
    """
    Get the detail of the location where the checklist was recorded.

    :param node: the Tag for the body of the Location section.

    :return: a dict containing the fields describing the location.

    """
    checklist = {
        'name': _get_site(node),
        'subnational2': _get_subnational2(node),
        'subnational1': _get_subnational1(node),
        'country': _get_country(node),
        'lat': _get_latitude(node),
        'lon': _get_longitude(node),
    }

    identifier = _get_location_identifier(node)
    if identifier:
        checklist['identifier'] = identifier

    return checklist


def _get_site(node):
    """
    Get the name of the site where the checklist was recorded.

    :param node: the Tag for the body of the Location section.

    :return: the name of the site.

    """
    tag = node.find('h5', class_='obs-loc')
    location = tag.text.split('( Map )')[0]
    site = location.rsplit(',', maxsplit=3)[0]
    return ' '.join(site.split())


def _get_subnational2(node):
    """
    Get the county where the checklist was recorded.

    :param node: the Tag for the body of the Location section.

    :return: the name of the county.

    """
    tag = node.find('h5', class_='obs-loc')
    location = tag.text.split('( Map )')[0]
    county = location.split(',')[-3].strip()
    return county


def _get_subnational1(node):
    """
    Get the region where the checklist was recorded.

    :param node: the Tag for the body of the Location section.

    :return: the name of the region.

    """
    tag = node.find('h5', class_='obs-loc')
    location = tag.text.split('( Map )')[0]
    region = location.split(',')[-2].strip()
    return region


def _get_country(node):
    """
    Get the country where the checklist was recorded.

    :param node: the Tag for the body of the Location section.

    :return: the two-letter ISO 8601 code doe the country.

    """
    tag = node.find('h5', class_='obs-loc')
    location = tag.text.split('( Map )')[0]
    country = location.split(',')[-1].strip()[:2]
    return country


def _get_location_identifier(node):
    """
    Get the unique identifier for the site if it is a hotspot.

    :param node: the Tag for the body of the Location section.

    :return: the unique identifier for the hotspot or None if it is not
    a hotspot.

    """
    identifier = None

    regex = re.compile(r'[Hh]otspot')
    tag = node.find('a', text=regex)

    if tag:
        url = tag['href']
        identifier = url.split('/')[-1]

    return identifier


def _get_latitude(node):
    """
    Get the latitude of the location.

    :param node: the Tag for the body of the Location section.

    :return: the signed latitude, positive values are north of the equator
    and negative ones are south of the equator.

    """
    tag = node.find('a', text='Map')
    url = tag['href']
    query = url.split('?')[1]
    params = query.split('&')
    coordinates = [param for param in params if param.startswith('ll=')][0]
    latitude = float(coordinates[3:].split(',')[0])
    return latitude


def _get_longitude(node):
    """
    Get the longitude of the location.

    :param node: the Tag for the body of the Location section.

    :return: the signed latitude, positive values are east of the prime
    meridian and negative ones are west of the prime meridian.

    """
    tag = node.find('a', text='Map')
    url = tag['href']
    query = url.split('?')[1]
    params = query.split('&')
    coordinates = [param for param in params if param.startswith('ll=')][0]
    longitude = float(coordinates[3:].split(',')[1])
    return longitude


def _point_protocol(node):
    """
    Get the effort for checklists following protocols where the observer(s)
    remain stationary.

    :param node: the tag for the body of the Date and Effort section.

    :return: the required and optional fields for the protocol.

    """
    results = {
        'time': _get_time(node),
        'duration': _get_duration(node),
        'party_size': _get_party_size(node),
        'observers': _get_observers(node),
    }

    if not results['time']:
        raise ValueError('the time field was not found')

    if not results['duration']:
        raise ValueError('the duration field was not found')

    if not results['party_size']:
        raise ValueError('the party size field was not found')

    return results


def _distance_protocol(node):
    """
    Get the effort for checklists following protocols where the observer(s)
    are moving.

    :param node: the tag for the body of the Date and Effort section.

    :return: the required and optional fields for the protocol.

    """
    results = {
        'time': _get_time(node),
        'duration': _get_duration(node),
        'distance': _get_distance(node),
        'party_size': _get_party_size(node),
        'observers': _get_observers(node),
    }

    if not results['time']:
        raise ValueError('the time field was not found')

    if results['duration'] is None:
        raise ValueError('the duration field was not found')

    if results['distance'] == (None, None):
        raise ValueError('the distance field was not found')

    if not results['party_size']:
        raise ValueError('the party size field was not found')

    return results


def _incidental_observations(node):
    """
    Get the effort for checklists with incidental observations.

    :param node: the tag for the body of the Date and Effort section.

    :return: the required and optional fields.

    """
    results = {
        'observers': _get_observers(node),
    }

    time = _get_time(node)
    if time:
        results['time'] = time

    return results


def _historical_observations(node):
    """
    Get the effort for checklists with historical records.

    All fields here are optional, except the observer submitting the
    checklist since any or no protocol may have been followed.

    :param node: the tag for the body of the Date and Effort section.

    :return: the required and optional fields for the protocol.

    """
    results = {
        'observers': _get_observers(node),
    }

    time = _get_time(node)
    if time:
        results['time'] = time

    duration = _get_duration(node)
    if duration:
        results['duration'] = duration

    distance = _get_distance(node)
    if distance != (None, None):
        results['distance'] = distance

    area = _get_area(node)
    if area != (None, None):
        results['area'] = area

    party_size = _get_party_size(node)
    if party_size:
        results['party_size'] = party_size

    return results


def _area_protocol(include_area=True):
    """
    Get the effort for checklists following protocols where the observer(s)
    are covering an area.

    A closure is used as the area field is optional for checklists that
    follow the Banding protocol so we avoid writing almost identical
    functions.

    :param include_area: the tag for the body of the Date and Effort section.

    :return: the required and optional fields for the protocol.

    """

    def _get_area_fields(node):
        results = {
            'time': _get_time(node),
            'area': _get_area(node),
            'duration': _get_duration(node),
            'party_size': _get_party_size(node),
            'observers': _get_observers(node),
        }

        if not results['time']:
            raise ValueError('the time field was not found')

        if include_area:
            if results['area'] == (None, None):
                raise ValueError('the area field was not found')
        else:
            del results['area']

        if results['duration'] is None:
            raise ValueError('the duration field was not found')

        if not results['party_size']:
            raise ValueError('the party size field was not found')

        return results

    return _get_area_fields


def _get_date_and_effort(node):
    """
    Get the date and details of the protocol, if any, used to create the checklist.

    :param node: the tag for the body of the Date and Effort section.

    :return: dict containing the checklist a
    """
    results = {
        'date': _get_date(node),
        'comment': _get_comment(node),
        'protocol': _get_protocol(node),
    }

    _get_effort = _get_date_and_effort.protocols[results['protocol']]
    results.update(_get_effort(node))

    return results


_get_date_and_effort.protocols = {
    'Stationary': _point_protocol,
    'Traveling': _distance_protocol,
    'Incidental': _incidental_observations,
    'Historical': _historical_observations,
    'Area': _area_protocol(),
    'Banding': _area_protocol(include_area=False),
    'eBird Pelagic Protocol': _distance_protocol,
    'Nocturnal Flight Call Count': _point_protocol,
    'Random': _distance_protocol,
    'CWC Point Count': _point_protocol,
    'CWC Area Count': _area_protocol(),
    'PROALAS': _point_protocol,
    'TNC California Waterbird Count': _point_protocol,
    'Rusty BlackbirdSpring Migration Blitz': _distance_protocol,
    'California Brown Pelican Survey': _distance_protocol,

}


def _get_protocol(node):
    """
    Get the method used to count the birds in the checklist.

    :param node: the Tag for the body of the Date and Effort section.

    :return: the name of the protocol used.

    """
    regex = re.compile(r'\s*[Pp]rotocol[:]?\s*')
    tag = node.find('dt', text=regex)
    field = tag.parent.dd
    protocol = field.text.strip().capitalize()
    return protocol


def _get_date(node):
    """
    Get the date the checklist was made.

    :param node: the Tag for the body of the Date and Effort section.

    :return: the date the checklist was recorded.

    """
    field = node.find('h5', class_='rep-obs-date')
    value = ' '.join(field.text.split()[:4])
    return datetime.datetime.strptime(value, '%a %b %d, %Y').date()


def _get_time(node):
    """
    Get the time the checklist was started.

    :param node: the Tag for the body of the Date and Effort section.

    :return: the time the checklist started. May be None for Incidental
    or Historical checklists.

    """
    time = None
    field = node.find('h5', class_='rep-obs-date')
    value = ' '.join(field.text.split()[4:])
    if value:
        time = datetime.datetime.strptime(value, '%I:%M %p').time()
    return time


def _get_party_size(node):
    """
    Get the number of observers.

    :param node: the Tag for the body of the Date and Effort section.

    :return: the number of people in the group.

    """
    count = None
    regex = re.compile(r'\s*[Pp]arty[\s]+[Ss]ize[:]?\s*')
    tag = node.find('dt', text=regex)
    if tag:
        field = tag.parent.dd
        count = int(field.text.strip())
    return count


def _get_distance(node):
    """
    Get the distance covered.

    :param node: the Tag for the body of the Date and Effort section.

    :return: a tuple containing the (floating-point) value and units for
    the distance covered, e.g (1.0, 'km') or (1.0, 'mi').

    """
    distance = None
    units = None

    regex = re.compile(r'\s*[Dd]istance[:]?\s*')
    tag = node.find('dt', text=regex)

    if tag:
        field = tag.parent.dd
        values = field.text.lower().split()
        distance = float(values[0])
        units = _get_distance.units[values[1]]

    return distance, units


_get_distance.units = {
    'kilometer(s)': 'km',
    'kilometre(s)': 'km',
    'km(s)':        'km',
    'kilometers':   'km',
    'kilometres':   'km',
    'km':           'km',
    'kms':          'km',
    'mile(s)':      'mi',
    'miles':        'mi',
}


def _get_area(node):
    """
    Get the area covered in hectares or acres.

    :param node: the Tag for the body of the Date and Effort section.

    :return: a tuple containing the (floating-point) value and units for
    the area covered, e.g (1.0, 'ha') or (1.0, 'acre').

    """
    area = None
    units = None

    regex = re.compile(r'\s*[Aa]rea[:]?\s*')
    tag = node.find('dt', text=regex)

    if tag:
        field = tag.parent.dd
        values = field.text.lower().split()
        area = float(values[0])
        units = _get_area.units[values[1]]

    return area, units


_get_area.units = {
    'hectare(s)': 'ha',
    'hectares':   'ha',
    'ha':         'ha',
    'acre(s)':    'acre',
    'acres':      'acre',
}


def _get_duration(node):
    """
    Get the time spent following the protocol.

    :param node: the Tag for the body of the Date and Effort section.

    :return: the time, in hours and minutes.

    """
    duration = None

    regex = re.compile(r'\s*[Dd]uration[:]?\s*')
    tag = node.find('dt', text=regex)

    if tag:
        field = tag.parent.dd
        values = field.text.lower().split()

        if 'minute(s)' in values:
            minutes = int(values[values.index('minute(s)') - 1])
        else:
            minutes = 0

        if 'hour(s)' in values:
            hours = int(values[values.index('hour(s)') - 1])
        else:
            hours = 0

        duration = datetime.timedelta(hours=hours, minutes=minutes)

    return duration


def _get_observers(node):
    """
    Get the list of observers.

    NOTE: this field only contains the name of the observer that submitted
    the checklist.

    :param node: the Tag for the body of the Date and Effort section.

    :return: the list of the observers' names.

    """
    observers = []

    regex = re.compile(r'\s*[Oo]bservers[:]?\s*')
    tag = node.find('dt', text=regex)
    field = tag.parent.dd
    name = ' '.join(field.text.split())
    observers.append(name)

    return observers


def _get_comment(node):
    """
    Get the comment about the checklist.

    :param node: the Tag for the body of the Date and Effort section.

    :return: the comment.

    """
    regex = re.compile(r'\s*[Cc]omment[:]?\s*')
    tag = node.find('dt', text=regex)

    comment = None

    if tag:
        field = tag.parent.dd
        comment = ' '.join(field.text.split()).capitalize()

    return comment


def _get_entries(node):
    """
    Get the list of species seen.

    :param node: the tag for body of the Species section.

    :return: a list of species seen.

    """
    entries = []
    tags = node.find_all('li', class_='spp-entry')
    for tag in tags:
        entries.append(_get_entry(tag))
    return entries


def _get_entry(node):
    """
    Get the details of each species seen.

    :param node: the tag for an entry in the list of species.

    :return: a dict containg the fields extracted.

    """
    return {
        'species': _get_species(node),
        'count': _get_count(node),
    }


def _get_species(node):
    """
    Get common name of the species seen.

    :param node: the tag for an entry in the list of species.

    :return: the species common name.

    """
    tag = node.find('h5', class_='se-name')
    value = ' '.join(tag.text.split())
    return value


def _get_count(node):
    """
    Get the count for the species seen.

    :param node: the tag for an entry in the list of species.

    :return: the number of birds seen or None if the species was present
    but not counted.

    """
    count = None
    tag = node.find('h5', class_='se-count')
    value = tag.text.strip().lower()
    if value != 'x':
        count = int(value)
    return count


def _get_complete(node):
    """
    Get flag indicating whether the checklist contains all species seen.

    :param node: the tag for the body of the last section in the checklist.

    :return: True is all species seen were recorded, False if not.

    """
    tag = node.find('div', class_='all-spp-ans').find('h5')
    value = tag.text.strip().lower()
    return value == 'yes'
