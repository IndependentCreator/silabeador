# Golden Dataset Testing for Silabeador

This directory contains a golden dataset testing system for the silabeador library. The golden dataset is generated from the Sharvard corpus and can be used for regression testing to ensure that changes to the library don't break existing functionality.

## Overview

The testing system consists of two main scripts:

1. **`generate_golden_data.py`** - Generates a golden dataset by running the current implementation on all words in the Sharvard corpus
2. **`test_golden_data.py`** - Tests the current implementation against a golden dataset to detect regressions

## Quick Start

### 1. Generate Golden Data

First, generate the golden dataset using the default parameters:

```bash
python generate_golden_data.py
```

This will create a `golden_data.json` file containing the syllabification and stress information for all words in the Sharvard corpus.

### 2. Run Tests

Test the current implementation against the golden data:

```bash
python test_golden_data.py
```

This will run all tests and report any differences between the current implementation and the golden data.

## Detailed Usage

### generate_golden_data.py

Generate a golden dataset from the Sharvard corpus.

```bash
python generate_golden_data.py [OPTIONS]
```

**Options:**

- `--corpus PATH` - Path to corpus file (default: `silabeador/sharvard.txt`)
- `--output PATH` - Output path for golden data (default: `golden_data.json`)
- `--exceptions {0,1,2}` - Level of exceptions handling (default: 1)
  - 0: No exceptions
  - 1: Basic exceptions
  - 2: Extended exceptions with special hiatus rules
- `--ipa` - Use IPA transcription rules
- `--h` - Treat 'h' as consonant
- `--epen` - Apply epenthesis
- `--tl` - Treat 'tl' as indivisible onset

**Examples:**

```bash
# Generate with default parameters
python generate_golden_data.py

# Generate with extended exceptions and IPA rules
python generate_golden_data.py --exceptions 2 --ipa --output golden_data_ipa.json

# Generate with Mexican Spanish 'tl' treatment
python generate_golden_data.py --tl --output golden_data_tl.json
```

### test_golden_data.py

Test the current implementation against a golden dataset.

```bash
python test_golden_data.py [OPTIONS]
```

**Options:**

- `--golden PATH` - Path to golden data file (default: `golden_data.json`)
- `-v, --verbose` - Print verbose output including passing tests
- `-s, --summary` - Only print summary (suppress test-by-test output)

**Examples:**

```bash
# Run tests with default golden data
python test_golden_data.py

# Run tests with verbose output
python test_golden_data.py --verbose

# Run tests with only summary output
python test_golden_data.py --summary

# Test against a different golden dataset
python test_golden_data.py --golden golden_data_ipa.json
```

## Golden Data Format

The golden dataset is stored as a JSON file with the following structure:

```json
{
  "metadata": {
    "corpus_file": "silabeador/sharvard.txt",
    "parameters": {
      "exceptions": 1,
      "ipa": false,
      "h": false,
      "epen": false,
      "tl": false
    },
    "total_sentences": 600,
    "total_words": 5000
  },
  "data": [
    {
      "line_number": 6,
      "sentence": "Hay gemas de gran valor en la tienda.",
      "words": [
        {
          "word": "Hay",
          "syllables": ["Hay"],
          "stress_index": -1,
          "syllabified": "Hay"
        },
        {
          "word": "gemas",
          "syllables": ["ge", "mas"],
          "stress_index": -2,
          "syllabified": "ge-mas"
        }
      ]
    }
  ]
}
```

### Fields:

- **metadata**: Information about how the golden data was generated
  - `corpus_file`: Path to the source corpus
  - `parameters`: The silabeador parameters used
  - `total_sentences`: Number of sentences processed
  - `total_words`: Total number of words in the dataset

- **data**: Array of sentences from the corpus
  - `line_number`: Line number in the original corpus file
  - `sentence`: The original sentence text
  - `words`: Array of word results
    - `word`: The original word
    - `syllables`: Array of syllables
    - `stress_index`: Index of stressed syllable (negative from end)
    - `syllabified`: Syllables joined with hyphens
    - `error`: (optional) Error message if syllabification failed

## Workflow

### Initial Setup (One-time)

1. Generate the initial golden dataset:
   ```bash
   python generate_golden_data.py
   ```

2. Review the golden data to ensure it's correct
3. Commit `golden_data.json` to version control

### During Development

1. Make changes to the silabeador code

2. Run tests to check for regressions:
   ```bash
   python test_golden_data.py
   ```

3. If tests fail:
   - If the changes are intentional improvements, regenerate the golden data:
     ```bash
     python generate_golden_data.py
     ```
   - If the changes are bugs, fix the code and retest

### Multiple Configuration Testing

You can maintain multiple golden datasets for different parameter combinations:

```bash
# Generate datasets for different configurations
python generate_golden_data.py --exceptions 0 --output golden_data_no_exceptions.json
python generate_golden_data.py --exceptions 1 --output golden_data_basic.json
python generate_golden_data.py --exceptions 2 --output golden_data_extended.json
python generate_golden_data.py --ipa --output golden_data_ipa.json

# Test against each configuration
python test_golden_data.py --golden golden_data_no_exceptions.json
python test_golden_data.py --golden golden_data_basic.json
python test_golden_data.py --golden golden_data_extended.json
python test_golden_data.py --golden golden_data_ipa.json
```

## Test Output

The test script provides colored output:

- ✓ Green: Test passed
- ✗ Red: Test failed (difference from golden data)
- ⚠ Yellow: Expected error

Example output:

```
Running tests with parameters:
  exceptions=1, ipa=False, h=False, epen=False, tl=False

Testing 5000 words from 600 sentences...

  ✓ Hay: Hay (stress: -1)
  ✓ gemas: ge-mas (stress: -2)
  ✗ palabra: Syllables differ: expected ['pa', 'la', 'bra'], got ['pa', 'lab', 'ra']

======================================================================
TEST SUMMARY
======================================================================

Total words tested: 5000
Passed: 4999 (99.98%)
Failed: 1

FAILURES:

  Line 42: palabra
    Expected: pa-la-bra (stress: -2)
    Got:      pa-lab-ra (stress: -2)
    Syllables differ: expected ['pa', 'la', 'bra'], got ['pa', 'lab', 'ra']

======================================================================
```

## Exit Codes

Both scripts return standard exit codes:

- `0`: Success (all tests passed)
- `1`: Failure (tests failed or errors occurred)

This allows integration with CI/CD systems:

```bash
# Example CI script
python generate_golden_data.py || exit 1
python test_golden_data.py || exit 1
```

## Notes

- The Sharvard corpus contains 700 Spanish sentences designed for speech intelligibility testing
- Each sentence is processed word by word, extracting only alphabetic Spanish characters
- Punctuation is stripped but the original sentence is preserved for reference
- The golden data format is human-readable JSON with proper UTF-8 encoding for Spanish characters

## About the Sharvard Corpus

The Sharvard Corpus is both a list of phonemically-balanced Spanish sentences and recordings of the full sentence set by a male and a female speaker.
These sentences are suitable for use in speech intelligibility testing. The corpus is described in the following paper:
V. Aubanel, M. L. García Lecumberri and M. Cooke (2014). The Sharvard corpus: A phonemically-balanced Spanish sentence resource for audiology. Int. J. Audiology 53: 633-638.
https://doi.org/10.3109/14992027.2014.907507
