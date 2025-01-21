import pytest
from pyslop.cronslator import cronslate
from io import StringIO
import sys


class TestBasicExamples:
    def test_simple_schedule(self):
        result = cronslate("Every Monday at 3am")
        assert result == "0 3 * * 1"

    def test_multiple_times(self):
        result = cronslate("Every day at 2am and 2pm")
        assert result == "0 2,14 * * *"

    def test_complex_schedule(self):
        result = cronslate("Every 30 minutes between 9am and 5pm on weekdays")
        assert result == "*/30 9-17 * * 1-5"


class TestErrorHandlingExamples:
    def test_invalid_hour(self):
        with pytest.raises(ValueError):
            cronslate("at 25:00")

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "",  # Empty string
            "invalid cron string",  # Nonsense input
            "at 25:00",  # Invalid hour
            "on day 32",  # Invalid day
        ],
    )
    def test_invalid_inputs(self, invalid_input):
        with pytest.raises(ValueError):
            cronslate(invalid_input)


class TestCompleteScriptExample:
    def test_process_schedules(self):
        # This test verifies the complete script example works as shown
        schedules = [
            "Every Monday at 3am",
            "Every weekday at noon",
            "Every 15 minutes",
            "First day of every month at midnight",
            "Every Sunday at 4:30 PM",
        ]

        expected_outputs = [
            "0 3 * * 1",
            "0 12 * * 1-5",
            "*/15 * * * *",
            "0 0 1 * *",
            "30 16 * * 0",
        ]

        # Test each schedule individually
        for schedule, expected in zip(schedules, expected_outputs):
            assert cronslate(schedule) == expected

        # Test the actual output formatting
        original_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Execute the example code
        print("Natural Language → Cron Expression")
        print("─" * 40)

        for schedule in schedules:
            try:
                cron = cronslate(schedule)
                print(f"{schedule:<30} → {cron}")
            except ValueError as e:
                print(f"{schedule:<30} → Error: {e}")

        sys.stdout = original_stdout
        output_lines = captured_output.getvalue().splitlines()

        # Verify output format
        assert "Natural Language → Cron Expression" in output_lines[0]
        assert "─" * 40 in output_lines[1]
        assert "Every Monday at 3am" in output_lines[2]
        assert "0 3 * * 1" in output_lines[2]


class TestReadmeTableExamples:
    """Tests for each example in the README table"""

    @pytest.mark.parametrize(
        "description,expected",
        [
            ("Every Monday at 3am", "0 3 * * 1"),
            ("Every weekday at noon", "0 12 * * 1-5"),
            ("Every 15 minutes", "*/15 * * * *"),
            ("First day of every month at midnight", "0 0 1 * *"),
            ("Every Sunday at 4:30 PM", "30 16 * * 0"),
            ("Every hour on the half hour", "30 * * * *"),
            ("Every day at 2am and 2pm", "0 2,14 * * *"),
            ("Every 30 minutes between 9am and 5pm on weekdays", "*/30 9-17 * * 1-5"),
            ("First Monday of every month at 3am", "0 3 1-7 * 1"),
            ("Every quarter hour between 2pm and 6pm", "*/15 14-18 * * *"),
            ("Every weekend at 10pm", "0 22 * * 0,6"),
            ("Every 5 minutes during business hours", "*/5 9-17 * * 1-5"),
            ("3rd day of every month at 1:30am", "30 1 3 * *"),
            ("Every weekday at 9am, 1pm and 5pm", "0 9,13,17 * * 1-5"),
            ("At midnight on Mondays and Fridays", "0 0 * * 1,5"),
            ("Twice daily at 6:30 and 18:30", "30 6,18 * * *"),
            ("Monthly on the 15th at noon", "0 12 15 * *"),
            ("Three times per hour at 15, 30, and 45 minutes", "15,30,45 * * * *"),
            ("Last day of month at 11:59 PM", "59 23 L * *"),
            ("Weekdays at quarter past each hour", "15 * * * 1-5"),
            ("Once per hour in the first 15 minutes", "0-14 * * * *"),
            ("Workdays at 8:45 AM except on the 13th", "45 8 1-12,14-31 * 1-5"),
            ("First 5 days of each quarter at dawn", "0 6 1-5 1,4,7,10 *"),
        ],
    )
    def test_readme_table_examples(self, description, expected):
        assert cronslate(description) == expected
