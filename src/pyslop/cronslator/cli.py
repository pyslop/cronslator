import sys
from pyslop.cronslator import cronslate


def print_usage():
    print("Usage:", file=sys.stderr)
    print("  cronslate 'Every Monday at 3am'", file=sys.stderr)
    print("  cronslate Every Monday at 3am", file=sys.stderr)
    print("  echo 'Every Monday at 3am' | cronslate", file=sys.stderr)


def main():
    # Check if input is being piped
    if not sys.stdin.isatty():
        try:
            description = sys.stdin.read().strip()
        except Exception as e:
            print(f"Error reading input: {e}", file=sys.stderr)
            sys.exit(1)
    # Check for command line arguments
    elif len(sys.argv) > 1:
        # If first argument is quoted, use it directly
        if len(sys.argv) == 2:
            description = sys.argv[1]
        # Otherwise join all arguments
        else:
            description = " ".join(sys.argv[1:])
    else:
        print_usage()
        sys.exit(1)

    if not description:
        print("Error: Empty input", file=sys.stderr)
        sys.exit(1)

    try:
        result = cronslate(description)
        print(result)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
