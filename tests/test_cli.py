import pytest
from unittest.mock import patch
import sys
from io import StringIO
from cronslator.cli import main


def test_cli_single_quoted_argument():
    test_input = ["cronslate", "Every Monday at 3am"]
    expected = "0 3 * * 1\n"

    with patch.object(sys, "argv", test_input), patch(
        "sys.stdin.isatty", return_value=True
    ), patch("sys.stdout", new=StringIO()) as fake_out:
        main()
        assert fake_out.getvalue() == expected


def test_cli_multiple_arguments():
    test_input = ["cronslate", "Every", "Monday", "at", "3am"]
    expected = "0 3 * * 1\n"

    with patch.object(sys, "argv", test_input), patch(
        "sys.stdin.isatty", return_value=True
    ), patch("sys.stdout", new=StringIO()) as fake_out:
        main()
        assert fake_out.getvalue() == expected


def test_cli_piped_input():
    test_input = "Every Monday at 3am"
    expected = "0 3 * * 1\n"

    # Create a mock stdin with our test input
    mock_stdin = StringIO(test_input)

    with patch("sys.stdin", mock_stdin), patch(
        "sys.stdin.isatty", return_value=False
    ), patch("sys.stdout", new=StringIO()) as fake_out, patch(
        "sys.stdin.read", return_value=test_input
    ):
        main()
        assert fake_out.getvalue() == expected


def test_cli_no_arguments():
    test_input = ["cronslate"]

    with patch("sys.stderr", new=StringIO()) as fake_err, patch(
        "sys.stdin.isatty", return_value=True
    ), patch.object(sys, "argv", test_input):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        assert "Usage:" in fake_err.getvalue()


def test_cli_empty_input():
    test_input = ["cronslate", ""]

    with patch("sys.stderr", new=StringIO()) as fake_err, patch(
        "sys.stdin.isatty", return_value=True
    ), patch.object(sys, "argv", test_input):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        assert "Error: Empty input" in fake_err.getvalue()


def test_cli_invalid_input():
    test_input = ["cronslate", "invalid cron string"]

    with patch("sys.stderr", new=StringIO()) as fake_err, patch(
        "sys.stdin.isatty", return_value=True
    ), patch.object(sys, "argv", test_input):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        assert "Error:" in fake_err.getvalue()
