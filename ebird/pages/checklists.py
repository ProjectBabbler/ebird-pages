import datetime
import re
import requests

from bs4 import BeautifulSoup


def get_checklist(identifier):
    """
    Get the data for a checklist from its eBird web page.

    Args:
        identifier (str): the unique identifier for the checklist, e.g. S62633426

    Returns:
        (dict): all the fields extracted from the web page.

    ToDo:
        * scrape entry comments.
        * scrape age/sex table
        * scrape uploaded media
        * scrape observers
        * update scraping of different protocols

    """
    url = "https://ebird.org/checklist/" + identifier
    response = requests.get(url)
    response.raise_for_status()
    return _scrape_checklist(response.text)


def _scrape_checklist(contents):
    soup = BeautifulSoup(contents, "lxml")
    return {
        'identifier': _scrape_identifier(soup),
        'date': _scrape_date(soup),
        'protocol': _scrape_protocol(soup),
        'location': _scrape_location(soup),
        'entries': _scrape_entries(soup),
        'comment': _scrape_comment(soup),
        'complete': _scrape_complete(soup)
    }


def _scrape_identifier(node):
    return node.find('input', {'name': 'subID'})['value']


def _scrape_location(node):
    node = node.find_all('section')[2]
    coords = _scrape_coords(node)
    return {
        'name': _scrape_site(node),
        'identifier': _scrape_location_identifier(node),
        'subnational2': _scrape_subnational2(node),
        'subnational2_code': _scrape_subnational2_code(node),
        'subnational1': _scrape_subnational1(node),
        'subnational1_code': _scrape_subnational1_code(node),
        'country': _scrape_country(node),
        'country_code': _scrape_country_code(node),
        'lat': float(coords[0]),
        'lon': float(coords[1]),
    }


def _scrape_site(node):
    tag = node.find('h6').parent.find('span')
    return tag.text.strip()


def _scrape_subnational2(node):
    node = node.find('span', {'class': 'is-visuallyHidden'})
    node = node.parent.find_all('li')[0]
    return node.find('a').text.strip()


def _scrape_subnational2_code(node):
    node = node.find('span', {'class': 'is-visuallyHidden'})
    node = node.parent.find_all('li')[0]
    url = node.find('a')['href']
    return url.split('/')[-1]


def _scrape_subnational1(node):
    node = node.find('span', {'class': 'is-visuallyHidden'})
    node = node.parent.find_all('li')[1]
    return node.find('a').text.strip()


def _scrape_subnational1_code(node):
    node = node.find('span', {'class': 'is-visuallyHidden'})
    node = node.parent.find_all('li')[1]
    url = node.find('a')['href']
    return url.split('/')[-1]


def _scrape_country(node):
    node = node.find('span', {'class': 'is-visuallyHidden'})
    node = node.parent.find_all('li')[2]
    return node.find('a').text.strip()


def _scrape_country_code(node):
    node = node.find('span', {'class': 'is-visuallyHidden'})
    node = node.parent.find_all('li')[2]
    url = node.find('a')['href']
    return url.split('/')[-1]


def _scrape_location_identifier(node):
    url = node.find('h6').parent.find('a')['href']
    return url.split('/')[-1]


def _scrape_coords(node):
    tag = node.find_all('a')[1]
    query = tag['href'].split('?')[1]
    param = query.split('&')[1]
    coords = param.split('=')[1]
    return coords.split(',')


def _point_protocol(node):
    results = {
        'time': _scrape_time(node),
        'duration': _scrape_duration(node),
        'party_size': _scrape_party_size(node),
        'observers': _scrape_observers(node),
    }

    if not results['time']:
        raise ValueError('the time field was not found')

    if not results['duration']:
        raise ValueError('the duration field was not found')

    if not results['party_size']:
        raise ValueError('the party size field was not found')

    return results


def _distance_protocol(node):
    results = {
        'time': _scrape_time(node),
        'duration': _scrape_duration(node),
        'distance': _scrape_distance(node),
        'party_size': _scrape_party_size(node),
        'observers': _scrape_observers(node),
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
    results = {
        'observers': _scrape_observers(node),
    }

    time = _scrape_time(node)
    if time:
        results['time'] = time

    return results


def _historical_observations(node):
    results = {
        'observers': _scrape_observers(node),
    }

    time = _scrape_time(node)
    if time:
        results['time'] = time

    duration = _scrape_duration(node)
    if duration:
        results['duration'] = duration

    distance = _scrape_distance(node)
    if distance != (None, None):
        results['distance'] = distance

    area = _scrape_area(node)
    if area != (None, None):
        results['area'] = area

    party_size = _scrape_party_size(node)
    if party_size:
        results['party_size'] = party_size

    return results


def _area_protocol(include_area=True):

    def _scrape_area_fields(node):
        results = {
            'time': _scrape_time(node),
            'area': _scrape_area(node),
            'duration': _scrape_duration(node),
            'party_size': _scrape_party_size(node),
            'observers': _scrape_observers(node),
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

    return _scrape_area_fields


_protocols = {
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


def _scrape_protocol(node):
    results = {
        'name': _scrape_protocol_name(node),
    }

    # TODO enable
    # results.update(_protocols[results['name']](node))

    return results


def _scrape_protocol_name(node):
    regex = re.compile(r'^Protocol: .*')
    tag = node.find('span', title=regex)
    return tag.text.strip()


def _scrape_date(node):
    value = node.find('time')['datetime']
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M")


def _scrape_time(node):
    time = None
    field = node.find('h5', class_='rep-obs-date')
    value = ' '.join(field.text.split()[4:])
    if value:
        time = datetime.datetime.strptime(value, '%I:%M %p').time()
    return time


def _scrape_party_size(node):
    count = None
    regex = re.compile(r'\s*[Pp]arty[\s]+[Ss]ize[:]?\s*')
    tag = node.find('dt', text=regex)
    if tag:
        field = tag.parent.dd
        count = int(field.text.strip())
    return count


def _scrape_distance(node):
    distance = None
    units = None

    regex = re.compile(r'\s*[Dd]istance[:]?\s*')
    tag = node.find('dt', text=regex)

    if tag:
        field = tag.parent.dd
        values = field.text.lower().split()
        distance = float(values[0])
        units = _scrape_distance.units[values[1]]

    return distance, units


_scrape_distance.units = {
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


def _scrape_area(node):
    area = None
    units = None

    regex = re.compile(r'\s*[Aa]rea[:]?\s*')
    tag = node.find('dt', text=regex)

    if tag:
        field = tag.parent.dd
        values = field.text.lower().split()
        area = float(values[0])
        units = _scrape_area.units[values[1]]

    return area, units


_scrape_area.units = {
    'hectare(s)': 'ha',
    'hectares':   'ha',
    'ha':         'ha',
    'acre(s)':    'acre',
    'acres':      'acre',
}


def _scrape_duration(node):
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


def _scrape_observers(node):
    observers = []

    regex = re.compile(r'\s*[Oo]bservers[:]?\s*')
    tag = node.find('dt', text=regex)
    field = tag.parent.dd
    name = ' '.join(field.text.split())
    observers.append(name)

    return observers


def _scrape_comment(node):
    section = node.find('h6', text='Checklist Comments').parent
    items = [p.text.strip() for p in section.find_all('p')]
    return ' '.join(items)


def _scrape_entries(node):
    entries = []
    node = node.find('main', {'id': 'list'})
    tags = node.find_all('li', {'data-observation': ''})
    for tag in tags:
        entries.append(_scrape_entry(tag))
    return entries


def _scrape_entry(node):
    return {
        'species': _scrape_species(node),
        'count': _scrape_count(node),
    }


def _scrape_species(node):
    node = node.find('div', {'class': 'Observation-species'})
    tag = node.find('span', {'class': 'Heading-main'})
    value = ' '.join(tag.text.split())
    return value


def _scrape_count(node):
    count = None
    node = node.find('div', class_='Observation-numberObserved')
    tag = node.find_all('span')[-1]
    value = tag.text.strip().lower()
    if value != 'x':
        count = int(value)
    return count


def _scrape_complete(node):
    regex = re.compile(r'^Protocol: .*')
    heading = node.find('span', title=regex).parent
    tag = heading.find('span', {'class': 'Badge-label'})
    value = tag.text.strip()
    return value == 'Complete'
