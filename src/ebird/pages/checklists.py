import datetime as dt
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
    url = _get_url(identifier)
    content = _get_page(url)
    root = _get_tree(content)
    return _get_checklist(root)


def _get_url(identifier):
    return "https://ebird.org/checklist/%s" % identifier


def _get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def _get_tree(content):
    return BeautifulSoup(content, "lxml")


def _get_checklist(root):
    return {
        'identifier': _get_identifier(root),
        'date': _get_date(root),
        'protocol': _get_protocol(root),
        'location': _get_location(root),
        'entries': _get_entries(root),
        'comment': _get_comment(root),
        'complete': _get_complete(root)
    }


def _get_location(root):
    return {
        'name': _get_location_name(root),
        'identifier': _get_location_identifier(root),
        'subnational2': _get_subnational2(root),
        'subnational2_code': _get_subnational2_code(root),
        'subnational1': _get_subnational1(root),
        'subnational1_code': _get_subnational1_code(root),
        'country': _get_country(root),
        'country_code': _get_country_code(root),
        'lat': _get_latitude(root),
        'lon': _get_longitude(root),
    }


# IMPORTANT: All the functions that extract values, start at the root of the
# tree, and each value is extracted independently. This reduces performance
# but makes updating the code when the page layout changes much much easier.
# The helper functions simplify navigating to a point in the tree where the
# data is located.

def _find_page_sections(root):
    return root.find_all("div", {"class": "Page-section"})


def _get_identifier(root):
    node = root.find('input', {'type': 'hidden', 'name': 'subID'})
    return node['value']


def _get_date(root):
    node = _find_page_sections(root)[1]
    value = node.find('time')['datetime']
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M")


def _get_coordinates(root):
    link = root.find(href=re.compile("www.google.com/maps"))
    query = link['href'].split('?')[1]
    param = query.split('&')[1]
    return param.split('=')[1]


def _get_latitude(root):
    return _get_coordinates(root).split(',')[0]


def _get_longitude(root):
    return _get_coordinates(root).split(',')[1]


def _get_location_root(root):
    node = _find_page_sections(root)[1]
    return node.find('span', string="Location")


def _get_location_name(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Location")
    if node.find_next_sibling('a'):
        node = node.find_next_sibling('a').find('span')
    else:
        node = node.find_next_sibling('span')
    return node.text.strip()


def _get_location_identifier(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Location")
    if node.find_next_sibling('a'):
        url = node.find_next_sibling('a')['href']
        return url.split('/')[-1]
    else:
        return ''


def _get_subnational2(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Region")
    node = node.find_next_sibling('ul').find_all('li')[0]
    return node.find('a').text.strip()


def _get_subnational2_code(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Region")
    node = node.find_next_sibling('ul').find_all('li')[0]
    url = node.find('a')['href']
    return url.split('/')[-1]


def _get_subnational1(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Region")
    node = node.find_next_sibling('ul').find_all('li')[1]
    return node.find('span').text.strip()


def _get_subnational1_code(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Region")
    node = node.find_next_sibling('ul').find_all('li')[1]
    url = node.find('a')['href']
    return url.split('/')[-1]


def _get_country(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Region")
    node = node.find_next_sibling('ul').find_all('li')[2]
    return node.find('span').text.strip()


def _get_country_code(root):
    node = _find_page_sections(root)[1]
    node = node.find('span', string="Region")
    node = node.find_next_sibling('ul').find_all('li')[2]
    url = node.find('a')['href']
    return url.split('/')[-1]


def _point_protocol(root):
    results = {
        'time': _get_time(root),
        'duration': _get_duration(root),
        'party_size': _get_party_size(root),
        'observers': _get_observers(root),
    }

    if not results['time']:
        raise ValueError('the time field was not found')

    if not results['duration']:
        raise ValueError('the duration field was not found')

    if not results['party_size']:
        raise ValueError('the party size field was not found')

    return results


def _distance_protocol(root):
    results = {
        'time': _get_time(root),
        'duration': _get_duration(root),
        'distance': _get_distance(root),
        'party_size': _get_party_size(root),
        'observers': _get_observers(root),
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
        'observers': _get_observers(node),
    }

    time = _get_time(node)
    if time:
        results['time'] = time

    return results


def _historical_observations(node):
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


def _get_protocol(root):
    results = {
        'name': _get_protocol_name(root),
    }

    # TODO enable
    # results.update(_protocols[results['name']](root))

    return results


def _get_protocol_name(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r'^Protocol:.*')
    node = node.find('div', title=regex)
    node = node.find_all('span')[1]
    return node.text.strip()


def _get_time(root):
    return _get_date(root).time()


def _get_duration(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r'^Duration:.*')
    node = node.find('div', title=regex)
    node = node.find_all('span')[1]
    value = node.text.strip()
    hours = value.split(",", 1)[0].strip().split(" ")[0]
    minutes = value.split(",", 1)[1].strip().split(" ")[0]
    duration = dt.timedelta(hours=int(hours), minutes=int(minutes))
    return duration


def _get_party_size(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r'^Observers:.*')
    node = node.find('div', title=regex)
    node = node.find_all('span')[1]
    return int(node.text.strip())


def _get_distance(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r'^Distance:.*')
    node = node.find('span', title=regex)
    node = node.find_all('span')[1]
    value = node.text.strip()
    distance = value.split(" ")[0]
    units = value.split(" ")[1]
    return float(distance), units


def _get_area(node):
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


def _get_observers(node):
    observers = []

    regex = re.compile(r'\s*[Oo]bservers[:]?\s*')
    tag = node.find('dt', text=regex)
    field = tag.parent.dd
    name = ' '.join(field.text.split())
    observers.append(name)

    return observers


def _get_comment(root):
    items = []
    if node := root.find(id='checklist-comments'):
        for p in node.find_next_siblings('p'):
            items.append(p.text.strip())
    return '\n'.join(items)


def _get_entries(root):
    node = _find_page_sections(root)[3]
    node = node.find('div', {'id': 'list'})
    tags = node.find_all('li', {'data-observation': ''})
    entries = []
    for tag in tags:
        entries.append(_get_entry(tag))
    return entries


def _get_entry(node):
    return {
        'species': _get_species(node),
        'count': _get_count(node),
    }


def _get_species(node):
    node = node.find('div', {'class': 'Observation-species'})
    tag = node.find('span', {'class': 'Heading-main'})
    value = ' '.join(tag.text.split())
    return value


def _get_count(node):
    count = None
    node = node.find('div', class_='Observation-numberObserved')
    tag = node.find_all('span')[-1]
    value = tag.text.strip().lower()
    if value != 'x':
        count = int(value)
    return count


def _get_complete(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r'^Protocol:.*')
    node = node.find('div', title=regex).parent
    node = node.find_next_sibling("div")
    node = node.find('span', {'class': 'Badge-label'})
    value = node.text.strip()
    return value == 'Complete'
