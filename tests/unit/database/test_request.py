"""
This file contains all unit tests for the endpoint-table in the database. (Corresponding to the
file: 'flask_monitoringdashboard/database/request.py')
"""
from __future__ import division  # can be removed once we leave python 2.7

import time
from datetime import datetime, timedelta

import pytest

from flask_monitoringdashboard.core.date_interval import DateInterval
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_requests
from flask_monitoringdashboard.database.endpoint import get_avg_duration, get_endpoints
from flask_monitoringdashboard.database.request import add_request, get_date_of_first_request, get_latencies_sample
from flask_monitoringdashboard.database.versions import get_versions


def test_get_latencies_sample(session, request_1, endpoint):
    interval = DateInterval(datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    data = get_latencies_sample(session, endpoint.id, interval, sample_size=500)
    assert data == [request_1.duration]


def test_add_request(endpoint):
    """Test whether the function returns the right values."""
    # For some reason, using the session-fixture here doesn't work.
    num_requests = len(endpoint.requests)
    with session_scope() as session:
        add_request(
            session,
            duration=200,
            endpoint_id=endpoint.id,
            ip='127.0.0.1',
            group_by=None,
            status_code=200,
        )
        assert count_requests(session, endpoint.id) == num_requests + 1


@pytest.mark.parametrize('request_1__time_requested', [datetime(2020, 2, 3)])
def test_get_versions(session, request_1):
    """Test whether the function returns the right values."""
    for version, first_request in get_versions(session):
        if version == request_1.version_requested:
            assert first_request == request_1.time_requested
            return
    assert False, "Shouldn't reach here"


def test_get_endpoints(session, endpoint):
    """Test whether the function returns the right values."""
    endpoints = get_endpoints(session)
    assert endpoint.name in [endpoint.name for endpoint in endpoints]


@pytest.mark.parametrize('request_1__time_requested', [datetime(1970, 1, 1)])
def test_get_date_of_first_request(session, request_1):
    """Test whether the function returns the right values."""
    total_seconds = int(time.mktime(request_1.time_requested.timetuple()))
    assert get_date_of_first_request(session) == total_seconds


def test_get_avg_duration(session, request_1, request_2, endpoint):
    assert get_avg_duration(session, endpoint.id) == (request_1.duration + request_2.duration) / 2