# cronslator

## Natural Language to Cron

A Python 3.9+ library to convert an English string to cron schedule.

## Important

> This is not the library you are looking for!

This codebase was generated entirely from prompting
GitHub Copilot (Clause 3.5 Sonnet) and has not been
audited, verified or even assumed to be correct.

This is an experiment to tinker with new shiny tools,
and to share what's possible using them -
your takeaway could be "Wow, that's nice!" or "Wow, that's crap!"
and either are fine.

Beyond this line, there is no human written text or code,
it is all LLM generated slop (hence the org name pyslop!).

## Installation

Install from PyPI using pipx (recommended):

```bash
# Install pipx if you haven't already
python -m pip install --user pipx
python -m pipx ensurepath

# Install from PyPI
pipx install pyslop-cronslator

# Or install from TestPyPI
pipx install --pip-args="--index-url https://test.pypi.org/simple/ --no-deps" pyslop-cronslator
```

Or install from PyPI using pip:

```bash
pip install pyslop-cronslator
```

Or install from source:

```bash
git clone https://github.com/pyslop/cronslator.git
cd cronslator
pip install .
```

## Development

Clone and set up development environment:

```bash
# Clone the repository
git clone https://github.com/pyslop/cronslator.git
cd cronslator

# Install poetry if you haven't already
pip install poetry

# Install dependencies and development dependencies
poetry install

# Run tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_readme_examples.py
```

### Publishing to PyPI

For maintainers, to publish a new version:

```bash
# Update version in pyproject.toml first, then:

# Build the package
poetry build

# Configure TestPyPI repository (one-time setup)
poetry config repositories.testpypi https://test.pypi.org/legacy/

# Publish to TestPyPI first (requires TestPyPI credentials)
poetry publish -r testpypi

# Test the package from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps pyslop-cronslator

# If everything looks good, publish to PyPI (requires PyPI credentials)
poetry publish

# Or do both build and publish in one step
poetry publish --build
```

## Understanding Cron Format

The cron expressions generated follow the standard 5-field format:

```ascii
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

Special characters:

- `*`: any value
- `,`: value list separator
- `-`: range of values
- `/`: step values
- `L`: last day of month (only in day of month field)

Examples:

| Natural Language Description | Cron Expression |
|----------------------------|-----------------|
| Every Monday at 3am | `0 3 * * 1` |
| Every weekday at noon | `0 12 * * 1-5` |
| Every 15 minutes | `*/15 * * * *` |
| First day of every month at midnight | `0 0 1 * *` |
| Every Sunday at 4:30 PM | `30 16 * * 0` |
| Every hour on the half hour | `30 * * * *` |
| Every day at 2am and 2pm | `0 2,14 * * *` |
| Every 30 minutes between 9am and 5pm on weekdays | `*/30 9-17 * * 1-5` |
| First Monday of every month at 3am | `0 3 1-7 * 1` |
| Every quarter hour between 2pm and 6pm | `*/15 14-18 * * *` |
| Every weekend at 10pm | `0 22 * * 0,6` |
| Every 5 minutes during business hours | `*/5 9-17 * * 1-5` |
| 3rd day of every month at 1:30am | `30 1 3 * *` |
| Every weekday at 9am, 1pm and 5pm | `0 9,13,17 * * 1-5` |
| At midnight on Mondays and Fridays | `0 0 * * 1,5` |
| Twice daily at 6:30 and 18:30 | `30 6,18 * * *` |
| Monthly on the 15th at noon | `0 12 15 * *` |
| Three times per hour at 15, 30, and 45 minutes | `15,30,45 * * * *` |
| Last day of month at 11:59 PM | `59 23 L * *` |
| Weekdays at quarter past each hour | `15 * * * 1-5` |
| Once per hour in the first 15 minutes | `0-14 * * * *` |
| Workdays at 8:45 AM except on the 13th | `45 8 1-12,14-31 * 1-5` |
| First 5 days of each quarter at dawn | `0 6 1-5 1,4,7,10 *` |

## Usage

### As a Command Line Tool

After installation, you can use the `cronslate` command:

```bash
# Basic usage
cronslate "Every Monday at 3am"
# Output: 0 3 * * 1

# Using quotes is optional for simple phrases
cronslate Every Monday at 3am
# Output: 0 3 * * 1

# Pipe input from other commands
echo "Every 15 minutes" | cronslate
# Output: */15 * * * *
```

### As a Python Library

Basic usage:

```python
from pyslop.cronslator import cronslate

# Simple schedule
result = cronslate("Every Monday at 3am")
print(result)  # Output: 0 3 * * 1

# Multiple times
result = cronslate("Every day at 2am and 2pm")
print(result)  # Output: 0 2,14 * * *

# Complex schedules
result = cronslate("Every 30 minutes between 9am and 5pm on weekdays")
print(result)  # Output: */30 9-17 * * 1-5
```

Error handling:

```python
from pyslop.cronslator import cronslate

try:
    # This will raise a ValueError
    result = cronslate("at 25:00")
except ValueError as e:
    print(f"Error: {e}")

# Invalid inputs will raise ValueError:
invalid_inputs = [
    "",                      # Empty string
    "invalid cron string",   # Nonsense input
    "at 25:00",             # Invalid hour
    "on day 32",            # Invalid day
]

for input_str in invalid_inputs:
    try:
        cronslate(input_str)
    except ValueError as e:
        print(f"'{input_str}' is invalid: {e}")
```

Complete script example:

```python
#!/usr/bin/env python3
from pyslop.cronslator import cronslate

def process_schedules():
    schedules = [
        "Every Monday at 3am",
        "Every weekday at noon",
        "Every 15 minutes",
        "First day of every month at midnight",
        "Every Sunday at 4:30 PM"
    ]
    
    print("Natural Language → Cron Expression")
    print("─" * 40)
    
    for schedule in schedules:
        try:
            cron = cronslate(schedule)
            print(f"{schedule:<30} → {cron}")
        except ValueError as e:
            print(f"{schedule:<30} → Error: {e}")

if __name__ == "__main__":
    process_schedules()

# Output:
# Natural Language → Cron Expression
# ─────────────────────────────────────────────
# Every Monday at 3am             → 0 3 * * 1
# Every weekday at noon          → 0 12 * * 1-5
# Every 15 minutes               → */15 * * *
# First day of every month...    → 0 0 1 * *
# Every Sunday at 4:30 PM        → 30 16 * * 0
```
