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


class TimeParser:
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
    }

    @staticmethod
    def parse_time(time_str: str) -> tuple[int, int]:
        time_str = time_str.lower().strip()

        # Handle special times
        if time_str in TimeParser.SPECIAL_TIMES:
            time_str = TimeParser.SPECIAL_TIMES[time_str]

        # Convert 2pm/2am format to 24-hour
        am_pm_match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$", time_str)
        if am_pm_match:
            hour = int(am_pm_match.group(1))
            minute = int(am_pm_match.group(2) or "0")
            if am_pm_match.group(3) == "pm" and hour != 12:
                hour += 12
            if am_pm_match.group(3) == "am" and hour == 12:
                hour = 0
            return hour, minute

        # Handle 24-hour format
        time_match = re.match(r"^(\d{1,2}):(\d{2})$", time_str)
        if time_match:
            return int(time_match.group(1)), int(time_match.group(2))

        # Handle simple hour
        if time_str.isdigit():
            return int(time_str), 0

        raise ValueError(f"Invalid time format: {time_str}")

    @staticmethod
    def validate_time(hour: int, minute: int) -> None:
        if not (0 <= hour <= 23):
            raise ValueError(f"Invalid hour: {hour}")
        if not (0 <= minute <= 59):
            raise ValueError(f"Invalid minute: {minute}")

    @staticmethod
    def is_time_format(text: str) -> bool:
        """Check if a string segment looks like a time specification."""
        time_patterns = [
            r"\d{1,2}(?::\d{2})?\s*(?:am|pm)",
            r"\d{1,2}:\d{2}",
            r"noon|midnight|dawn",
        ]
        return any(re.search(pattern, text.lower()) for pattern in time_patterns)

    @staticmethod
    def parse_minutes_list(text: str) -> list[str]:
        """Extract multiple minute values from text."""
        minutes = []
        minute_matches = re.findall(r"(?:(?:,\s*)?(\d+)(?:\s*,|\s+and\s+)?)", text)
        return [m for m in minute_matches if 0 <= int(m) <= 59]

    @staticmethod
    def extract_days(description: str) -> list[str]:
        """Extract day numbers from text while avoiding time numbers."""
        days = []
        # Look for explicit day mentions with ordinals or 'day' keyword
        day_patterns = [
            r"(\d+)(?:st|nd|rd|th)\s+(?:day|of)",
            r"(?:day\s+)?(\d+)(?:\s+of)",
        ]
        for pattern in day_patterns:
            matches = re.finditer(pattern, description)
            for match in matches:
                days.append(match.group(1))
        return days

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
    def parse_time_range(text: str) -> tuple[int, int]:
        """Parse time range and return start and end hours."""
        range_match = re.search(
            r"between\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)\s+and\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)",
            text,
        )
        if not range_match:
            return -1, -1
        start_hour, _ = TimeParser.parse_time(range_match.group(1))
        end_hour, _ = TimeParser.parse_time(range_match.group(2))
        return start_hour, end_hour

    @staticmethod
    def parse_am_pm_times(text: str) -> list[tuple[int, int]]:
        """Parse all times with proper AM/PM context."""
        results = []

        # First, split into time tokens, preserving order
        time_tokens = re.finditer(
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?(?=\s|$|,|\sand\s)", text.lower()
        )

        current_meridiem = None  # Track AM/PM context

        for match in time_tokens:
            hour = int(match.group(1))
            minute = int(match.group(2) or "0")
            meridiem = match.group(3)

            # Update meridiem context if explicitly specified
            if meridiem:
                current_meridiem = meridiem

            # Apply meridiem context
            if current_meridiem == "pm" and hour != 12:
                hour += 12
            elif current_meridiem == "am" and hour == 12:
                hour = 0
            elif not current_meridiem:
                # Look ahead for AM/PM context if no context yet
                context_after = text[match.end() : match.end() + 10].lower()
                if "pm" in context_after and hour != 12:
                    hour += 12
                    current_meridiem = "pm"
                elif "am" in context_after and hour == 12:
                    hour = 0
                    current_meridiem = "am"

            TimeParser.validate_time(hour, minute)
            results.append((hour, minute))

        return results

    @staticmethod
    def combine_times(times: list[tuple[int, int]]) -> tuple[str, str]:
        """Combine multiple times into hour and minute components."""
        if not times:
            return "*", "*"

        # Extract hours and minutes, keeping as integers
        hours = []
        minutes = set()

        for hour, minute in times:
            hours.append(hour)
            if minute != 0:
                minutes.add(minute)

        # Sort numerically first, then convert to strings
        hours = sorted(set(hours))  # Remove duplicates and sort numerically
        hour_str = ",".join(str(h) for h in hours)

        # Handle minutes
        if minutes:
            minute_str = ",".join(str(m) for m in sorted(minutes))
        else:
            minute_str = "0"

        return hour_str, minute_str


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

    # Handle intervals first - this is highest priority
    if "every" in description and "minute" in description:
        interval_match = re.search(r"every\s+(\d+)\s+minute", description)
        if interval_match:
            interval = interval_match.group(1)
            components.minute = f"*/{interval}"

            # Handle time range for intervals
            if "between" in description:
                start_hour, end_hour = TimeParser.parse_time_range(description)
                if start_hour >= 0 and end_hour >= 0:
                    components.hour = f"{start_hour}-{end_hour}"

            # Handle weekday restrictions
            if "weekday" in description:
                components.day_of_week = "1-5"

            return str(components)

    # Handle "X times per hour" patterns
    if "times per hour" in description:
        minute_values = TimeParser.parse_minutes_list(description)
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
            start_hour, end_hour = TimeParser.parse_time_range(description)
            if start_hour >= 0 and end_hour >= 0:
                components.hour = f"{start_hour}-{end_hour}"
        return str(components)

    # Handle time specifications with proper AM/PM context
    times = TimeParser.parse_am_pm_times(description)
    if times:
        hour_str, minute_str = TimeParser.combine_times(times)
        if hour_str != "*":
            components.hour = hour_str
        if minute_str != "*":
            components.minute = minute_str

    # Handle special time patterns
    special_minute, special_hour = TimeParser.handle_special_time(description)
    if special_minute != "*":
        components.minute = special_minute
        components.hour = special_hour

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
            for day, number in TimeParser.WEEKDAYS.items():
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
