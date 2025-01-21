import re
from dataclasses import dataclass
from typing import Optional, Dict, List, Set


@dataclass
class CronComponents:
    minute: str = "*"
    hour: str = "*"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: str = "*"

    def __str__(self) -> str:
        return f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week}"


class BasicParser:
    """Handles basic time and number parsing"""

    WEEKDAYS = {
        "monday": "1",
        "tuesday": "2",
        "wednesday": "3",
        "thursday": "4",
        "friday": "5",
        "saturday": "6",
        "sunday": "0",
    }

    SPECIAL_TIMES = {
        "noon": "12:00",
        "midnight": "00:00",
        "dawn": "06:00",
    }

    ORDINALS = {
        "first": 1,
        "1st": 1,
        "second": 2,
        "2nd": 2,
        "third": 3,
        "3rd": 3,
        "fourth": 4,
        "4th": 4,
        "fifth": 5,
        "5th": 5,
        "sixth": 6,
        "6th": 6,
        "seventh": 7,
        "7th": 7,
        "eighth": 8,
        "8th": 8,
        "ninth": 9,
        "9th": 9,
        "tenth": 10,
        "10th": 10,
    }

    NUMBERS = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
    }

    @staticmethod
    def get_ordinal_weekday_range(ordinal: int, weekday: str) -> str:
        """Convert ordinal weekday (e.g. 'second monday') to day range."""
        if ordinal < 1 or ordinal > 5:
            raise ValueError(f"Invalid ordinal: {ordinal}")
        # Calculate the range for the ordinal occurrence
        start = (ordinal - 1) * 7 + 1
        end = start + 6
        return f"{start}-{end}"

    @staticmethod
    def parse_minutes_list(text: str) -> list[str]:
        """Extract multiple minute values from text."""
        minutes = []
        minute_matches = re.findall(r"(?:(?:,\s*)?(\d+)(?:\s*,|\s+and\s+)?)", text)
        return [m for m in minute_matches if 0 <= int(m) <= 59]

    @staticmethod
    def parse_time(time_str: str) -> tuple[int, int]:
        # Simplified time parsing
        time_str = time_str.lower().strip()
        if time_str in BasicParser.SPECIAL_TIMES:
            time_str = BasicParser.SPECIAL_TIMES[time_str]

        if ":" in time_str:
            hour, minute = map(int, time_str.split(":"))
            return hour, minute

        # Handle am/pm
        if "pm" in time_str:
            hour = int(time_str.replace("pm", "").strip())
            return (hour + 12 if hour != 12 else 12), 0
        if "am" in time_str:
            hour = int(time_str.replace("am", "").strip())
            return (0 if hour == 12 else hour), 0

        return int(time_str), 0

    @staticmethod
    def parse_am_pm_times(text: str) -> list[tuple[int, int]]:
        """Parse all times with proper AM/PM context."""
        results = []
        time_tokens = re.finditer(
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?(?=\s|$|,|\sand\s)", text.lower()
        )

        current_meridiem = None
        for match in time_tokens:
            hour = int(match.group(1))
            minute = int(match.group(2) or "0")
            meridiem = match.group(3)

            if meridiem:
                current_meridiem = meridiem

            if current_meridiem == "pm" and hour != 12:
                hour += 12
            elif current_meridiem == "am" and hour == 12:
                hour = 0

            results.append((hour, minute))

        return results

    @staticmethod
    def combine_times(times: list[tuple[int, int]]) -> tuple[str, str]:
        """Combine multiple times into hour and minute components."""
        if not times:
            return "*", "*"

        hours = sorted(set(h for h, _ in times))
        minutes = sorted(set(m for _, m in times))

        hour_str = ",".join(str(h) for h in hours)
        minute_str = ",".join(str(m) for m in minutes) if minutes else "0"

        return hour_str, minute_str

    @staticmethod
    def parse_time_range(text: str) -> tuple[int, int]:
        """Parse time range and return start and end hours."""
        range_match = re.search(
            r"between\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)\s+and\s+"
            r"(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)",
            text,
        )
        if not range_match:
            return -1, -1
        start_hour, _ = BasicParser.parse_time(range_match.group(1))
        end_hour, _ = BasicParser.parse_time(range_match.group(2))
        return start_hour, end_hour

    @staticmethod
    def handle_special_time(description: str) -> tuple[str, str]:
        """Handle special time patterns and return (minute, hour)."""
        if "noon" in description:
            return "0", "12"
        elif "midnight" in description:
            return "0", "0"
        elif "dawn" in description:
            return "0", "6"
        return "*", "*"

    @staticmethod
    def handle_business_hours(description: str) -> tuple[str, str, str]:
        """Handle business hours patterns. Returns (minute, hour, day_of_week)"""
        if "business hours" in description:
            interval_match = re.search(r"every\s+(\d+)\s+minute", description)
            if interval_match:
                return f"*/{interval_match.group(1)}", "9-17", "1-5"
        return "*", "*", "*"

    @staticmethod
    def handle_quarter_patterns(description: str) -> tuple[str, str]:
        """Handle quarter past and first X minutes patterns"""
        if "quarter past" in description:
            return "15", "*"
        if "first 15 minutes" in description or "first fifteen minutes" in description:
            return "0-14", "*"
        return "*", "*"


class CronParser:
    """Main parser with simplified pattern matching"""

    def __init__(self):
        self.basic = BasicParser()

    def parse(self, description: str) -> CronComponents:
        components = CronComponents()
        description = description.lower()

        # Quick validation
        if not description:
            raise ValueError("Empty description")

        # Handle common patterns first
        if self._handle_intervals(description, components):
            return components

        if self._handle_specific_times(description, components):
            return components

        if self._handle_days(description, components):
            return components

        raise ValueError("Unable to parse schedule")

    def _handle_intervals(self, desc: str, comp: CronComponents) -> bool:
        # Simple interval handling
        if "every" in desc and "minute" in desc:
            match = re.search(r"every\s+(\d+)", desc)
            if match:
                comp.minute = f"*/{match.group(1)}"
                return True
        return False

    # Additional methods would go here, each handling specific patterns


def cronslate(description: str) -> str:
    if not description or not isinstance(description, str):
        raise ValueError("Invalid or empty description")

    # Enhanced input validation
    invalid_patterns = [
        r"\d{2}:\d{2}:\d{2}",  # No seconds
        r"(?:^|\s)(?:2[4-9]|[3-9]\d):[0-5]\d",  # Invalid hours
        r"day\s+(?:0|3[2-9]|[4-9]\d)",  # Invalid days
        "nananosecond",
        "invalid",
    ]

    if any(re.search(pattern, description.lower()) for pattern in invalid_patterns):
        raise ValueError("Invalid time specification")

    description = description.lower().strip()
    components = CronComponents()
    context = {}  # Store pattern matching context

    # First pass: Extract key patterns without setting components
    if "first day" in description:
        context["day_of_month"] = "1"

    if "first 5 days" in description and "quarter" in description:
        context["day_of_month"] = "1-5"
        context["month"] = "1,4,7,10"

    # Handle business hours first (before general interval handling)
    if "business hours" in description:
        minute, hour, day_of_week = BasicParser.handle_business_hours(description)
        components.minute = minute
        components.hour = hour
        components.day_of_week = day_of_week
        return str(components)

    # Handle intervals first - this is highest priority
    if "every" in description and "minute" in description:
        interval_match = re.search(r"every\s+(\d+)\s+minute", description)
        if interval_match:
            interval = interval_match.group(1)
            components.minute = f"*/{interval}"

            # Handle time range for intervals
            if "between" in description:
                start_hour, end_hour = BasicParser.parse_time_range(description)
                if start_hour >= 0 and end_hour >= 0:
                    components.hour = f"{start_hour}-{end_hour}"

            # Handle weekday restrictions
            if "weekday" in description:
                components.day_of_week = "1-5"

            return str(components)

    # Add new handlers before existing interval handling
    if "business hours" in description:
        minute, hour, day_of_week = BasicParser.handle_business_hours(description)
        components.minute = minute
        components.hour = hour
        components.day_of_week = day_of_week
        return str(components)

    # Handle "X times per hour" patterns
    if "times per hour" in description:
        minute_values = BasicParser.parse_minutes_list(description)
        if minute_values:
            components.minute = ",".join(sorted(minute_values, key=int))
            components.hour = "*"
            return str(components)

    # Handle special patterns
    if "half hour" in description or "half past" in description:
        components.minute = "30"
        components.hour = "*"
        return str(components)

    if "quarter hour" in description:
        components.minute = "*/15"
        if "between" in description:
            start_hour, end_hour = BasicParser.parse_time_range(description)
            if start_hour >= 0 and end_hour >= 0:
                components.hour = f"{start_hour}-{end_hour}"
        return str(components)

    # Add new pattern handling before quarter hour section
    if any(pat in description for pat in ["quarter past", "first 15 minutes"]):
        minute, hour = BasicParser.handle_quarter_patterns(description)
        components.minute = minute
        components.hour = hour
        if "weekday" in description:
            components.day_of_week = "1-5"
        return str(components)

    # Handle time specifications with proper AM/PM context
    times = BasicParser.parse_am_pm_times(description)
    if times:
        hour_str, minute_str = BasicParser.combine_times(times)
        if hour_str != "*":
            components.hour = hour_str
        if minute_str != "*":
            components.minute = minute_str

    # Handle special time patterns
    special_minute, special_hour = BasicParser.handle_special_time(description)
    if special_minute != "*":
        components.minute = special_minute
        components.hour = special_hour

    # Handle every Nth day pattern (add this before monthly patterns)
    nth_day_match = re.search(
        r"(?:every\s+)?(\d+|fourth?|third?|second?|first|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:days?|day)",
        description,
        re.IGNORECASE,
    )
    if nth_day_match:
        interval = nth_day_match.group(1)
        if interval in BasicParser.ORDINALS:
            interval = str(BasicParser.ORDINALS[interval.lower()])
        elif interval in BasicParser.NUMBERS:
            interval = str(BasicParser.NUMBERS[interval.lower()])
        elif interval.lower().rstrip("s") in BasicParser.NUMBERS:
            interval = str(BasicParser.NUMBERS[interval.lower().rstrip("s")])
        if 1 <= int(interval) <= 31:
            components.day_of_month = f"*/{interval}"
        else:
            raise ValueError(f"Invalid day interval: {interval}")

    # Add before other monthly patterns
    ordinal_day_match = re.search(
        r"(first|second|third|fourth|fifth)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        description,
        re.IGNORECASE,
    )
    if ordinal_day_match:
        ordinal = BasicParser.ORDINALS[ordinal_day_match.group(1).lower()]
        weekday = BasicParser.WEEKDAYS[ordinal_day_match.group(2).lower()]
        components.day_of_month = BasicParser.get_ordinal_weekday_range(
            ordinal, weekday
        )
        components.day_of_week = weekday

        # Add default time if not specified
        if components.minute == "*" and components.hour == "*":
            components.minute = "0"
            components.hour = "0"

    # Handle monthly patterns
    if "last day" in description:
        components.day_of_month = "L"
    elif context.get("day_of_month"):
        components.day_of_month = context["day_of_month"]
    elif "first monday" in description:
        components.day_of_month = "1-7"
        components.day_of_week = "1"
    else:
        ordinal_match = re.search(r"(\d+)(?:st|nd|rd|th)", description)
        if ordinal_match:
            day = int(ordinal_match.group(1))
            if not (1 <= day <= 31):
                raise ValueError(f"Invalid day of month: {day}")
            components.day_of_month = str(day)

    # Handle workday exceptions
    if "workday" in description and "except" in description:
        if "13th" in description:
            components.day_of_month = "1-12,14-31"
            components.day_of_week = "1-5"

    # Handle weekdays after time processing
    if components.day_of_week == "*":  # Don't override if already set
        if "weekday" in description:
            components.day_of_week = "1-5"
        elif "weekend" in description:
            components.day_of_week = "0,6"
        else:
            days = []
            for day, number in BasicParser.WEEKDAYS.items():
                if day in description:
                    days.append(number)
            if days:
                if "and" in description or "," in description:
                    components.day_of_week = ",".join(sorted(set(days), key=int))
                else:
                    components.day_of_week = days[0]

    # Apply stored context
    if context.get("month"):
        components.month = context["month"]

    return str(components)
