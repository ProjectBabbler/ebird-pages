import pytest

# Skip the remaining tests if one fails.
# This way we don't end up hitting the the eBird site excessively,
# since we want to investigate the checklist that failed.


def pytest_sessionstart(session):
    session.failednames = set()


def pytest_runtest_makereport(item, call):
    if call.excinfo is not None:
        item.session.failednames.add(item.originalname)


def pytest_runtest_setup(item):
    if item.originalname in item.session.failednames:
        pytest.skip()
