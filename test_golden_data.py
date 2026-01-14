#!/usr/bin/env python3
"""
Golden Dataset Test Suite for silabeador

This script tests the current implementation of silabeador against a golden
dataset to detect any regressions or changes in behavior.

Usage:
    python test_golden_data.py [--golden golden_data.json] [--verbose] [--summary]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import silabeador


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class TestResult:
    """Container for test results"""
    def __init__(self):
        self.total_words = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.failures: List[Dict] = []
        self.new_errors: List[Dict] = []


def load_golden_data(golden_path: Path) -> Dict:
    """Load golden dataset from JSON file"""
    with open(golden_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compare_results(word: str, expected: Dict, actual_syllables: List[str],
                   actual_stress: int) -> Tuple[bool, str]:
    """
    Compare expected and actual results for a word.

    Returns:
        Tuple of (success: bool, message: str)
    """
    if 'error' in expected:
        # The word had an error in golden data
        return True, f"Skipped (had error in golden data: {expected['error']})"

    differences = []

    # Compare syllables
    if expected['syllables'] != actual_syllables:
        differences.append(
            f"Syllables differ: expected {expected['syllables']}, got {actual_syllables}"
        )

    # Compare stress index
    if expected['stress_index'] != actual_stress:
        differences.append(
            f"Stress differs: expected {expected['stress_index']}, got {actual_stress}"
        )

    if differences:
        return False, '; '.join(differences)

    return True, "OK"


def run_tests(golden_data: Dict, verbose: bool = False) -> TestResult:
    """
    Run tests against golden dataset.

    Args:
        golden_data: The golden dataset dictionary
        verbose: Whether to print verbose output

    Returns:
        TestResult object with test statistics
    """
    result = TestResult()
    params = golden_data['metadata']['parameters']

    print(f"\n{Colors.BOLD}Running tests with parameters:{Colors.RESET}")
    print(f"  exceptions={params['exceptions']}, ipa={params['ipa']}, "
          f"h={params['h']}, epen={params['epen']}, tl={params['tl']}")
    print(f"\n{Colors.BOLD}Testing {golden_data['metadata']['total_words']} words "
          f"from {golden_data['metadata']['total_sentences']} sentences...{Colors.RESET}\n")

    # Process each sentence in the golden data
    for sentence_data in golden_data['data']:
        line_num = sentence_data['line_number']

        if verbose:
            print(f"\n{Colors.BLUE}Line {line_num}: {sentence_data['sentence']}{Colors.RESET}")

        for word_data in sentence_data['words']:
            result.total_words += 1
            word = word_data['word']

            try:
                # Run silabeador on the word
                actual_syllables = silabeador.syllabify(
                    word,
                    exceptions=params['exceptions'],
                    ipa=params['ipa'],
                    h=params['h'],
                    epen=params['epen'],
                    tl=params['tl']
                )
                actual_stress = silabeador.tonica(
                    word,
                    exceptions=params['exceptions'],
                    ipa=params['ipa'],
                    h=params['h'],
                    epen=params['epen'],
                    tl=params['tl']
                )

                # Compare results
                success, message = compare_results(word, word_data, actual_syllables, actual_stress)

                if success:
                    result.passed += 1
                    if verbose:
                        print(f"  {Colors.GREEN}✓{Colors.RESET} {word}: {'-'.join(actual_syllables)} "
                              f"(stress: {actual_stress})")
                else:
                    result.failed += 1
                    result.failures.append({
                        'line': line_num,
                        'word': word,
                        'expected': word_data,
                        'actual_syllables': actual_syllables,
                        'actual_stress': actual_stress,
                        'message': message
                    })
                    print(f"  {Colors.RED}✗{Colors.RESET} {word}: {message}")

            except Exception as e:
                result.errors += 1
                # Check if this was an expected error
                if 'error' not in word_data:
                    result.new_errors.append({
                        'line': line_num,
                        'word': word,
                        'error': str(e)
                    })
                    print(f"  {Colors.RED}✗{Colors.RESET} {word}: ERROR - {e}")
                elif verbose:
                    print(f"  {Colors.YELLOW}⚠{Colors.RESET} {word}: (error was expected)")

    return result


def print_summary(result: TestResult):
    """Print test summary with statistics"""
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")

    total = result.total_words
    passed = result.passed
    failed = result.failed
    errors = result.errors

    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\nTotal words tested: {total}")
    print(f"{Colors.GREEN}Passed: {passed} ({pass_rate:.1f}%){Colors.RESET}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    if errors > 0:
        print(f"{Colors.YELLOW}Errors: {errors}{Colors.RESET}")

    # Print failure details if there are any
    if result.failures:
        print(f"\n{Colors.BOLD}FAILURES:{Colors.RESET}")
        for failure in result.failures:
            print(f"\n  Line {failure['line']}: {Colors.RED}{failure['word']}{Colors.RESET}")
            print(f"    Expected: {failure['expected']['syllabified']} (stress: {failure['expected']['stress_index']})")
            print(f"    Got:      {'-'.join(failure['actual_syllables'])} (stress: {failure['actual_stress']})")
            print(f"    {failure['message']}")

    # Print new errors if there are any
    if result.new_errors:
        print(f"\n{Colors.BOLD}NEW ERRORS (not in golden data):{Colors.RESET}")
        for error in result.new_errors:
            print(f"\n  Line {error['line']}: {Colors.RED}{error['word']}{Colors.RESET}")
            print(f"    Error: {error['error']}")

    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    # Return exit code
    return 0 if (failed == 0 and len(result.new_errors) == 0) else 1


def main():
    parser = argparse.ArgumentParser(
        description='Test silabeador against golden dataset'
    )
    parser.add_argument(
        '--golden',
        type=Path,
        default=Path('golden_data.json'),
        help='Path to golden data file (default: golden_data.json)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print verbose output including passing tests'
    )
    parser.add_argument(
        '-s', '--summary',
        action='store_true',
        help='Only print summary (suppress test-by-test output)'
    )

    args = parser.parse_args()

    if not args.golden.exists():
        print(f"{Colors.RED}Error: Golden data file not found: {args.golden}{Colors.RESET}")
        return 1

    # Load golden data
    print(f"Loading golden data from {args.golden}...")
    golden_data = load_golden_data(args.golden)

    # Run tests
    result = run_tests(golden_data, verbose=args.verbose and not args.summary)

    # Print summary
    exit_code = print_summary(result)

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
