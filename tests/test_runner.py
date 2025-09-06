#!/usr/bin/env python3
"""Test runner for OpenBioCure Connectors Core."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=True, markers=None):
    """Run tests with specified configuration."""

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add coverage if requested
    if coverage:
        cmd.extend([
            "--cov=obc_connector_sdk",
            "--cov=obc_ingestion",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])

    # Add markers if specified
    if markers:
        cmd.extend(["-m", markers])

    # Select test type
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    elif test_type == "connectors":
        cmd.append("tests/connectors/")
    elif test_type == "smoke":
        cmd.extend(["-m", "smoke"])
    elif test_type == "regression":
        cmd.extend(["-m", "regression"])
    else:  # all
        cmd.append("tests/")

    # Add additional options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])

    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd)


def run_connector_tests(connector_name=None, network=False):
    """Run connector-specific tests."""

    cmd = ["python", "-m", "pytest"]

    if connector_name:
        cmd.append(f"tests/connectors/test_{connector_name}_connector.py")
    else:
        cmd.append("tests/connectors/")

    if not network:
        cmd.extend(["-m", "not network"])

    cmd.extend(["-v", "--tb=short"])

    print(f"Running connector tests: {' '.join(cmd)}")
    return subprocess.run(cmd)


def run_linting():
    """Run code linting."""

    print("Running code linting...")

    # Run flake8
    flake8_cmd = ["python", "-m", "flake8", "obc_connector_sdk", "obc_ingestion", "connectors"]
    flake8_result = subprocess.run(flake8_cmd)

    # Run mypy
    mypy_cmd = ["python", "-m", "mypy", "obc_connector_sdk", "obc_ingestion"]
    mypy_result = subprocess.run(mypy_cmd)

    return flake8_result.returncode == 0 and mypy_result.returncode == 0


def run_formatting():
    """Run code formatting."""

    print("Running code formatting...")

    # Run black
    black_cmd = ["python", "-m", "black", "obc_connector_sdk", "obc_ingestion", "connectors", "tests"]
    black_result = subprocess.run(black_cmd)

    # Run isort
    isort_cmd = ["python", "-m", "isort", "obc_connector_sdk", "obc_ingestion", "connectors", "tests"]
    isort_result = subprocess.run(isort_cmd)

    return black_result.returncode == 0 and isort_result.returncode == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test runner for OpenBioCure Connectors Core")

    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "connectors", "smoke", "regression"],
        default="all",
        help="Type of tests to run"
    )

    parser.add_argument(
        "--connector",
        help="Specific connector to test"
    )

    parser.add_argument(
        "--network",
        action="store_true",
        help="Include network tests"
    )

    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--markers", "-m",
        help="Pytest markers to run"
    )

    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting"
    )

    parser.add_argument(
        "--format",
        action="store_true",
        help="Run code formatting"
    )

    parser.add_argument(
        "--all-checks",
        action="store_true",
        help="Run all checks (tests, linting, formatting)"
    )

    args = parser.parse_args()

    # Run formatting first if requested
    if args.format or args.all_checks:
        if not run_formatting():
            print("❌ Code formatting failed")
            sys.exit(1)
        print("✅ Code formatting completed")

    # Run linting if requested
    if args.lint or args.all_checks:
        if not run_linting():
            print("❌ Linting failed")
            sys.exit(1)
        print("✅ Linting completed")

    # Run tests
    if args.connector:
        result = run_connector_tests(args.connector, args.network)
    else:
        result = run_tests(
            test_type=args.type,
            verbose=args.verbose,
            coverage=not args.no_coverage,
            markers=args.markers
        )

    if result.returncode == 0:
        print("✅ All tests passed")
    else:
        print("❌ Tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
