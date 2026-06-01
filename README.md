# Deletion Theme Helper

Find crossword answers where **removing letters from a word leaves another real word**.

For example, deleting **RA** from **CARAMEL** gives **CAMEL**. This tool finds all such pairs automatically.

---

## Setup

You need Python 3 and a word list file. Two options:

- **Plain text** — one word per line (like `example_dictionary.txt` included here)
- **Scored `.dict`** — CrossFire / Crossword Compiler format, e.g. `spreadthewordlist_caps.dict`

---

## Basic Usage

### 1. Find words that contain your pattern

```
python deletion_theme.py --pattern RA --find example_dictionary.txt
```

Prints every word in the list that contains **RA**.

---

### 2. See what each word deletes to

Add `--show-deletion-result`:

```
python deletion_theme.py --pattern RA --find example_dictionary.txt --show-deletion-result
```

Output looks like:
```
CARAMEL  ->  CAMEL
BARRAGE  ->  BARGE
DEFRAY   ->  DEFY
```

Words with no valid deletion are shown as `(no valid deletion)`.

---

### 3. Use a scored word list

If you have a `.dict` file, use `--min-score` to keep only good-quality words.
Scores in `spreadthewordlist_caps.dict` run from 0 (avoid) to 50 (best).

```
python deletion_theme.py --pattern RA --find "C:\Users\Stephen\Downloads\spreadthewordlist_caps.dict" --min-score 50 --show-deletion-result
```

---

### 4. Validate your own list of phrases

Have a text file of candidate entries, one per line? Check which ones work:

```
python deletion_theme.py --pattern RA --validate my_phrases.txt example_dictionary.txt --show-deletion-result
```

`my_phrases.txt` is your candidates. `example_dictionary.txt` is used to check that the result is a real word.

---

## Pipelining

Chain two commands together: **find** candidates, then **validate** that the result is also a good word.

```
python deletion_theme.py --pattern RA --find example_dictionary.txt | python deletion_theme.py --pattern RA --validate - example_dictionary.txt --show-deletion-result
```

The `-` in `--validate -` means *read from the previous command's output*.

With a scored `.dict` file, this makes both sides use quality words only:

```
python deletion_theme.py --pattern RA --find "C:\Users\Stephen\Downloads\spreadthewordlist_caps.dict" --min-score 50 | python deletion_theme.py --pattern RA --validate - "C:\Users\Stephen\Downloads\spreadthewordlist_caps.dict" --min-score 50 --show-deletion-result
```

---

## Useful Filters

| Flag | What it does |
|------|-------------|
| `--min-score 50` | Only use words scored 50 or above (`.dict` files only) |
| `--min-len 5` | Source word must be at least 5 letters |
| `--len 7` | Source word must be exactly 7 letters |
| `--result-len 5` | Word after deletion must be exactly 5 letters |
| `--all` | Show every valid deletion per word, not just the first |

---

## Pattern Ideas

| Pattern | Finds |
|---------|-------|
| `RA` | Words containing RA |
| `THE` | Words containing THE |
| `[AEIOU]{2}` | Any two vowels in a row |
| `(.)\1` | Any doubled letter (e.g. SS, TT) |
| `ING` | Words containing ING |
