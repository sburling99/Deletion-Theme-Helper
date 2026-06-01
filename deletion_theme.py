#!/usr/bin/env python3
"""
Crossword deletion theme helper.

Searches a dictionary for words matching a regex pattern, and validates that
deleting the matched text produces a real word.

Two modes:
  --find DICT...    List every word in DICT whose letters contain a match
                    for the pattern.
  --validate FILE   Given candidate words/phrases, keep those where deleting
                    a pattern match from any one word yields a valid
                    dictionary word.  Multi-word phrases are checked
                    word-by-word.

Plain-text word lists (free):
  ENABLE2K  https://www.wordgamedictionary.com/enable/
  TWL06     https://www.wordgamedictionary.com/twl06/
  SOWPODS   https://www.wordgamedictionary.com/sowpods/

Scored .dict files (CrossFire / Crossword Compiler format):
  Peter Broda       https://peterbroda.me/crosswords/wordlist/
  XWord Info        https://www.xwordinfo.com/WordList
  Spread the Word   https://www.spreadthewordlist.com/

.dict file format (CrossFire / Crossword Compiler):
  Each non-blank, non-comment line is one of:
    WORD;SCORE      semicolon-separated (primary CrossFire format, score 1-100)
    WORD<TAB>SCORE  tab-separated
    WORD            unscored entry
  Lines starting with '#' are treated as comments and skipped.
  Use --min-score to filter by score quality threshold.

Examples:
  # All RA-containing words from a plain-text list (NORA theme):
  python deletion_theme.py --pattern RA --find example_dictionary.txt

  # Same search using a scored CrossFire .dict file:
  python deletion_theme.py --pattern RA --find wordlist.dict

  # Only consider high-quality entries (score >= 50):
  python deletion_theme.py --pattern RA --find wordlist.dict --min-score 50

  # Mix a scored .dict file with a plain-text list:
  python deletion_theme.py --pattern RA --find wordlist.dict example_dictionary.txt --min-score 50

  # Any double-letter deletion (SSTRESS -> STRESS):
  python deletion_theme.py --pattern "(.)\1" --find example_dictionary.txt --show-deletion-result

  # Words where deleting a vowel pair leaves a real word:
  python deletion_theme.py --pattern "[AEIOU]{2}" --find example_dictionary.txt --show-deletion-result

  # Validate a candidate phrase list:
  python deletion_theme.py --pattern RA --validate phrases.txt example_dictionary.txt --show-deletion-result

  # Chain: find then validate:
  python deletion_theme.py --pattern RA --find example_dictionary.txt | \
      python deletion_theme.py --pattern RA --validate - example_dictionary.txt --show-deletion-result
"""

import re
import sys
import argparse


def _parse_dict_line(line):
    """
    Parse one line from a scored .dict file (CrossFire / Crossword Compiler format).

    Supported line forms (matched case-insensitively):
      WORD;SCORE      — semicolon-separated (primary CrossFire format)
      WORD<TAB>SCORE  — tab-separated
      WORD            — unscored entry

    Caller should strip the line and skip blank lines / '#' comments before
    calling this function.

    Returns (word_uppercase, score_or_None).
    Returns (None, None) if the line cannot yield a valid alphabetic token.
    """
    upper = line.upper().strip()
    if not upper or upper.startswith('#'):
        return None, None

    # Detect separator: semicolon takes priority over tab
    if ';' in upper:
        parts = upper.split(';', 1)
        token = parts[0].strip()
        try:
            score = int(parts[1].strip())
        except (ValueError, IndexError):
            score = None
    elif '\t' in upper:
        parts = upper.split('\t', 1)
        token = parts[0].strip()
        try:
            score = int(parts[1].strip())
        except (ValueError, IndexError):
            score = None
    else:
        # No separator — bare word, possibly followed by whitespace
        token = upper.split()[0] if upper else None
        score = None

    return token, score


def load_wordset(paths, min_score=None):
    """
    Build a set of valid uppercase words from one or more word-list files.

    File format is auto-detected by extension:
      .dict  — CrossFire / Crossword Compiler scored format (see _parse_dict_line)
      other  — plain text: one word per line; only the first whitespace-separated
               token on each line is used (compatible with ENABLE, TWL, SOWPODS, etc.)

    min_score : int or None
        When set, entries from .dict files whose score is *known* and strictly
        below this threshold are excluded.  Unscored .dict entries are always
        included (score unknown, not "bad").  Ignored for plain-text files.
    """
    words = set()
    for path in paths:
        is_dict = path != '-' and path.lower().endswith('.dict')
        fh = sys.stdin if path == '-' else open(path, encoding='utf-8', errors='ignore')
        try:
            for line in fh:
                stripped = line.strip()
                # Skip blank lines and comment lines (# prefix, common in .dict files)
                if not stripped or stripped.startswith('#'):
                    continue

                if is_dict:
                    token, score = _parse_dict_line(stripped)
                    if not token:
                        continue
                    # Exclude scored entries that fall below the threshold;
                    # unscored entries (score is None) pass through unconditionally.
                    if min_score is not None and score is not None and score < min_score:
                        continue
                else:
                    token = stripped.upper().split()[0]

                if token.isalpha():
                    words.add(token)
        finally:
            if path != '-':
                fh.close()
    return words


def load_phrases(path):
    fh = sys.stdin if path == '-' else open(path, encoding='utf-8', errors='ignore')
    phrases = [line.strip().upper() for line in fh if line.strip()]
    if path != '-':
        fh.close()
    return phrases


def all_deletions(word, pattern):
    """
    Yield (result, span) for every non-overlapping match of pattern in word,
    where result is word with that match removed.
    """
    for m in pattern.finditer(word):
        yield word[:m.start()] + word[m.end():], m.span()


def validate_phrase(phrase, pattern, valid_words, min_result=3, result_len=None, show_all=False):
    """
    For a (possibly multi-word) phrase, return result phrases where deleting
    one pattern match from one word leaves a valid dictionary word.
    """
    words = phrase.replace('-', ' ').split()
    results = []
    seen = set()

    for i, word in enumerate(words):
        for deleted, span in all_deletions(word, pattern):
            if len(deleted) < min_result or deleted not in valid_words:
                continue
            if result_len is not None and len(deleted) != result_len:
                continue
            new_phrase = ' '.join(words[:i] + [deleted] + words[i + 1:])
            if new_phrase not in seen:
                seen.add(new_phrase)
                results.append(new_phrase)
                if not show_all:
                    return results

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Crossword deletion theme helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('--pattern', metavar='REGEX', default='RA',
                        help='Regex pattern to find and delete (default: RA). '
                             'Matched against uppercase words.')

    parser.add_argument('dictionaries', nargs='+', metavar='DICT',
                        help='Word list file(s) used as the valid-word set. '
                             'Accepts plain-text files (.txt, etc.) and scored '
                             '.dict files (CrossFire / Crossword Compiler format).')

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--find', action='store_true',
                      help='List all words in DICT that contain a pattern match. '
                           'Add --show-deletion-result to also print the deleted form.')
    mode.add_argument('--validate', metavar='FILE',
                      help='Candidate word/phrase file; keep entries where a '
                           'pattern deletion yields a valid word. Use - for stdin.')

    parser.add_argument('--min-score', type=int, default=None, metavar='N',
                        help='For scored .dict files: exclude words whose score '
                             'is below N (1-100). Unscored entries are always kept. '
                             'Has no effect on plain-text word lists.')
    parser.add_argument('--min-len', type=int, default=4,
                        help='Min length of source word (default: 4).')
    parser.add_argument('--len', type=int, default=None, dest='exact_len',
                        help='Exact length of source word to match.')
    parser.add_argument('--min-result', type=int, default=3,
                        help='Min length of word after deletion (default: 3).')
    parser.add_argument('--result-len', type=int, default=None,
                        help='Exact length of word after deletion to match.')
    parser.add_argument('--show-deletion-result', action='store_true',
                        dest='show_result',
                        help='Print  ORIGINAL  ->  RESULT  pairs.')
    parser.add_argument('--all', dest='show_all', action='store_true',
                        help='Show every valid deletion per entry, not just the first.')

    args = parser.parse_args()

    try:
        pattern = re.compile(args.pattern.upper())
    except re.error as e:
        sys.exit(f'Invalid regex pattern: {e}')

    valid_words = load_wordset(args.dictionaries, min_score=args.min_score)

    if args.find:
        for word in sorted(
            w for w in valid_words
            if pattern.search(w)
            and len(w) >= args.min_len
            and (args.exact_len is None or len(w) == args.exact_len)
        ):
            if args.show_result:
                results = validate_phrase(word, pattern, valid_words,
                                          min_result=args.min_result,
                                          result_len=args.result_len,
                                          show_all=args.show_all)
                if results:
                    for result in results:
                        print(f'{word}  ->  {result}')
                else:
                    print(f'{word}  ->  (no valid deletion)')
            else:
                print(word)

    else:  # --validate
        for phrase in load_phrases(args.validate):
            results = validate_phrase(phrase, pattern, valid_words,
                                      min_result=args.min_result,
                                      result_len=args.result_len,
                                      show_all=args.show_all)
            if not results:
                continue
            if args.show_result:
                for result in results:
                    print(f'{phrase}  ->  {result}')
            else:
                print(phrase)


if __name__ == '__main__':
    main()
