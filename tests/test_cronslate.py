import pytest
from pyslop.cronslator import cronslate


@pytest.mark.parametrize(
    "description,expected",
    [
        ("Every Monday at 3am", "0 3 * * 1"),
        ("Every weekday at noon", "0 12 * * 1-5"),
        ("Every 15 minutes", "*/15 * * * *"),
        ("First day of every month at midnight", "0 0 1 * *"),
        ("Every Sunday at 4:30 PM", "30 16 * * 0"),
        ("Every fourth day at noon", "0 12 */4 * *"),
        ("Every four days at 11 pm", "0 23 */4 * *"),
    ],
)
def test_basic_schedules(description, expected):
    assert cronslate(description) == expected


@pytest.mark.parametrize(
    "description,expected",
    [
        ("Every hour on the half hour", "30 * * * *"),
        ("Every day at 2am and 2pm", "0 2,14 * * *"),
        ("Every 30 minutes between 9am and 5pm on weekdays", "*/30 9-17 * * 1-5"),
        ("Every quarter hour between 2pm and 6pm", "*/15 14-18 * * *"),
        ("Every weekend at 10pm", "0 22 * * 0,6"),
    ],
)
def test_complex_time_schedules(description, expected):
    assert cronslate(description) == expected


@pytest.mark.parametrize(
    "description,expected",
    [
        ("First Monday of every month at 3am", "0 3 1-7 * 1"),
        ("3rd day of every month at 1:30am", "30 1 3 * *"),
        ("Monthly on the 15th at noon", "0 12 15 * *"),
        ("Last day of month at 11:59 PM", "59 23 L * *"),
        ("Every second Sunday", "0 0 8-14 * 0"),  # Add this test case
        ("Every second Sunday at 2pm", "0 14 8-14 * 0"),  # And this variation
    ],
)
def test_monthly_schedules(description, expected):
    assert cronslate(description) == expected


@pytest.mark.parametrize(
    "description,expected",
    [
        ("Every weekday at 9am, 1pm and 5pm", "0 9,13,17 * * 1-5"),
        ("At midnight on Mondays and Fridays", "0 0 * * 1,5"),
        ("Twice daily at 6:30 and 18:30", "30 6,18 * * *"),
        ("Three times per hour at 15, 30, and 45 minutes", "15,30,45 * * * *"),
    ],
)
def test_multiple_time_schedules(description, expected):
    assert cronslate(description) == expected


@pytest.mark.parametrize(
    "description",
    [
        "",
        "invalid cron string",
        "every nananosecond",
        "at 25:00",
        "on day 32 of the month",
    ],
)
def test_invalid_inputs(description):
    with pytest.raises(ValueError):
        cronslate(description)


def test_case_insensitivity():
    assert cronslate("EVERY MONDAY AT 3AM") == "0 3 * * 1"
    assert cronslate("every SUNDAY at 4:30 pm") == "30 16 * * 0"


@pytest.mark.parametrize(
    "description,expected",
    [
        ("First 5 days of each quarter at dawn", "0 6 1-5 1,4,7,10 *"),
        ("Workdays at 8:45 AM except on the 13th", "45 8 1-12,14-31 * 1-5"),
        ("Second Monday of every month at midnight", "0 0 8-14 * 1"),
    ],
)
def test_advanced_schedules(description, expected):
    assert cronslate(description) == expected


@pytest.mark.parametrize(
    "description,expected",
    [
        # Add missing examples from README
        ("Every 5 minutes during business hours", "*/5 9-17 * * 1-5"),
        ("Weekdays at quarter past each hour", "15 * * * 1-5"),
        ("Once per hour in the first 15 minutes", "0-14 * * * *"),
    ],
)
def test_additional_schedules(description, expected):
    assert cronslate(description) == expected
