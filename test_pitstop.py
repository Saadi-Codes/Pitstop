import pytest
from pitstop import conversion_to_localtime, fetch_races, fetch_timezones
from datetime import datetime

def test_conversion_to_localtime():
    utc_time = "2023-05-18T15:00:00Z"
    user_timezone = "Europe/London"
    expected_local_time = "18-05-2023 16:00"
    assert conversion_to_localtime(utc_time, user_timezone) == expected_local_time

def test_conversion_to_localtime_ny():
    utc_time = "2023-05-18T15:00:00Z"
    user_timezone = "America/New_York"
    expected_local_time = "18-05-2023 11:00"
    assert conversion_to_localtime(utc_time, user_timezone) == expected_local_time

def test_conversion_to_localtime_sydney():
    utc_time = "2024-01-20T02:30:00Z"
    user_timezone = "Australia/Sydney"
    expected_local_time = "20-01-2024 13:30"
    assert conversion_to_localtime(utc_time, user_timezone) == expected_local_time

def test_conversion_to_localtime_tokyo():
    utc_time = "2023-12-01T08:00:00Z"
    user_timezone = "Asia/Tokyo"
    expected_local_time = "01-12-2023 17:00"
    assert conversion_to_localtime(utc_time, user_timezone) == expected_local_time


if __name__ == "__main__":
    import pytest
    pytest.main()
