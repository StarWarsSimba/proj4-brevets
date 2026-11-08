from nose.tools import assert_equal, raises
from acp_times import open_time, close_time
from datetime import datetime, timezone

def test_basic_opening_time():
    """Test opening time for 60km control on 200km brevet"""
    start = datetime(2024, 1, 1, 0, 0)
    result = open_time(60, 200, start)
    expected = datetime(2024, 1, 1, 1, 46).replace(tzinfo=timezone.utc).isoformat()  # 60/34 = 1:46
    assert_equal(result, expected)

def test_200km_closing_special_rule():
    """Test that 200km finish closes at 13:30, not 13:20"""
    start = datetime(2024, 1, 1, 0, 0)
    result = close_time(200, 200, start)
    expected = datetime(2024, 1, 1, 13, 30).replace(tzinfo=timezone.utc).isoformat()
    assert_equal(result, expected)

def test_multiple_speed_ranges():
    """Test control at 350km spanning two speed ranges"""
    start = datetime(2024, 1, 1, 0, 0)
    result = open_time(350, 600, start)
    # (200/34) + (150/32) = 5:53 + 4:41 = 10:34
    expected = datetime(2024, 1, 1, 10, 34).replace(tzinfo=timezone.utc).isoformat()
    assert_equal(result, expected)

def test_control_beyond_brevet():
    """Test control beyond brevet distance uses brevet distance"""
    start = datetime(2024, 1, 1, 0, 0)
    result_205 = open_time(205, 200, start)
    result_200 = open_time(200, 200, start)
    assert_equal(result_205, result_200)

@raises(ValueError)
def test_invalid_brevet_distance():
    """Test that invalid brevet distance raises error"""
    start = datetime(2024, 1, 1, 0, 0)
    open_time(100, 250, start)  # 250 is not a valid brevet