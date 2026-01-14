#!/usr/bin/env python3
"""
Golden Dataset Generator for silabeador

This script processes the sharvard.txt corpus and generates a golden dataset
of expected syllabification and stress outputs. The golden data can be used
as a regression test suite to ensure changes to the library don't break
existing functionality.

Usage:
    python generate_golden_data.py [--output golden_data.json] [--exceptions 1] [--ipa] [--h] [--epen] [--tl]
"""

import argparse
import json
import re
from pathlib import Path
import silabeador


def extract_words_from_corpus(corpus_path):
    """
    Extract all words from the sharvard.txt corpus file.

    Args:
        corpus_path: Path to the corpus file

    Returns:
        List of tuples (line_number, sentence, words)
    """
    with open(corpus_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    corpus_data = []
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Extract words from the sentence
        # Remove punctuation but keep the original sentence for reference
        words = re.findall(r'[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+', line)

        if words:
            corpus_data.append({
                'line_number': line_num,
                'sentence': line,
                'words': words
            })

    return corpus_data


def generate_golden_data(corpus_path, exceptions=1, ipa=False, h=False, epen=False, tl=False):
    """
    Generate golden dataset by running silabeador on all words in the corpus.

    Args:
        corpus_path: Path to the corpus file
        exceptions: Level of exceptions handling (0: none, 1: basic, 2: extended)
        ipa: Use IPA transcription rules
        h: Treat 'h' as consonant
        epen: Apply epenthesis
        tl: Treat 'tl' as indivisible onset

    Returns:
        Dictionary containing golden data with metadata
    """
    corpus_data = extract_words_from_corpus(corpus_path)

    golden_data = {
        'metadata': {
            'corpus_file': str(corpus_path),
            'parameters': {
                'exceptions': exceptions,
                'ipa': ipa,
                'h': h,
                'epen': epen,
                'tl': tl
            },
            'total_sentences': len(corpus_data),
            'total_words': sum(len(item['words']) for item in corpus_data)
        },
        'data': []
    }

    # Process each sentence
    for item in corpus_data:
        sentence_data = {
            'line_number': item['line_number'],
            'sentence': item['sentence'],
            'words': []
        }

        # Process each word in the sentence
        for word in item['words']:
            try:
                syllables = silabeador.syllabify(word, exceptions, ipa, h, epen, tl)
                stress_index = silabeador.tonica(word, exceptions, ipa, h, epen, tl)

                word_data = {
                    'word': word,
                    'syllables': syllables,
                    'stress_index': stress_index,
                    'syllabified': '-'.join(syllables)
                }
                sentence_data['words'].append(word_data)

            except Exception as e:
                # If there's an error, record it
                word_data = {
                    'word': word,
                    'error': str(e)
                }
                sentence_data['words'].append(word_data)

        golden_data['data'].append(sentence_data)

    return golden_data


def main():
    parser = argparse.ArgumentParser(
        description='Generate golden dataset from sharvard.txt corpus'
    )
    parser.add_argument(
        '--corpus',
        type=Path,
        default=Path('silabeador/sharvard.txt'),
        help='Path to the corpus file (default: silabeador/sharvard.txt)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('golden_data.json'),
        help='Output path for golden data (default: golden_data.json)'
    )
    parser.add_argument(
        '--exceptions',
        type=int,
        choices=[0, 1, 2],
        default=1,
        help='Level of exceptions handling (default: 1)'
    )
    parser.add_argument(
        '--ipa',
        action='store_true',
        help='Use IPA transcription rules'
    )
    parser.add_argument(
        '--h',
        action='store_true',
        help='Treat h as consonant'
    )
    parser.add_argument(
        '--epen',
        action='store_true',
        help='Apply epenthesis'
    )
    parser.add_argument(
        '--tl',
        action='store_true',
        help='Treat tl as indivisible onset'
    )

    args = parser.parse_args()

    if not args.corpus.exists():
        print(f"Error: Corpus file not found: {args.corpus}")
        return 1

    print(f"Generating golden data from {args.corpus}...")
    print(f"Parameters: exceptions={args.exceptions}, ipa={args.ipa}, h={args.h}, epen={args.epen}, tl={args.tl}")

    golden_data = generate_golden_data(
        args.corpus,
        exceptions=args.exceptions,
        ipa=args.ipa,
        h=args.h,
        epen=args.epen,
        tl=args.tl
    )

    # Write to output file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(golden_data, f, ensure_ascii=False, indent=2)

    print(f"\nGolden data generated successfully!")
    print(f"Total sentences: {golden_data['metadata']['total_sentences']}")
    print(f"Total words: {golden_data['metadata']['total_words']}")
    print(f"Output saved to: {args.output}")

    return 0


if __name__ == '__main__':
    exit(main())
