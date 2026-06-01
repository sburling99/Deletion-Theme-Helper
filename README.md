# Deletion Theme Helper

Find crossword answers where **removing letters from a word leaves another real word**.

For example, deleting **RA** from **CARAMEL** gives **CAMEL**.

The key strength of this tool: it doesn't just find words that *contain* your pattern — it checks the result against the same dictionary to confirm the leftover is also a real word.

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

Lists every word containing **RA**. Does **not** yet check if the deletion leaves a real word.

---

### 2. Only show words where the deletion is also a real word

Add `--valid-only`:

```
python deletion_theme.py --pattern RA --find example_dictionary.txt --valid-only
```

This is where the dictionary check kicks in. Only words like CARAMEL (→ CAMEL) come through — words where deletion leads nowhere are dropped silently.

---

### 3. Show both the original and what it deletes to

Add `--show-deletion-result` (implies `--valid-only` — no noise):

```
python deletion_theme.py --pattern RA --find example_dictionary.txt --show-deletion-result
```

Output:
```
CARAMEL  ->  CAMEL
BARRAGE  ->  BARGE
DEFRAY   ->  DEFY
```

---

### 4. Use a scored word list

If you have a `.dict` file, use `--min-score` to keep only good-quality words.
Scores in `spreadthewordlist_caps.dict` run from 0 (avoid) to 50 (best).

```
python deletion_theme.py --pattern RA --find "C:\Users\Stephen\Downloads\spreadthewordlist_caps.dict" --min-score 50 --show-deletion-result
```

---

### 5. Validate your own list of phrases

Have a text file of candidate entries, one per line? Check which ones work:

```
python deletion_theme.py --pattern RA --validate my_phrases.txt example_dictionary.txt --show-deletion-result
```

`my_phrases.txt` is your candidates. `example_dictionary.txt` is used to confirm the deletion result is a real word.

This also handles **multi-word phrases** — it checks each word in the phrase individually.

---

## Pipelining

### What's the difference between `--show-deletion-result` and pipelining?

`--find --show-deletion-result` scans the dictionary for candidates *and* validates them — but the candidates can only be words already in that same dictionary.

**Pipelining lets you use a completely different source of candidates.**

For example:

- You have a personal list of answers you're considering for a grid
- You want to check them against a stricter dictionary (not themselves)
- The deletion result should exist in a competition word list, not just the themed one

**Basic pipeline** — find candidates, then filter to only valid deletions:

```
python deletion_theme.py --pattern RA --find example_dictionary.txt | python deletion_theme.py --pattern RA --validate - example_dictionary.txt --show-deletion-result
```

The `-` means *read candidates from the previous command*.

**Cross-dictionary pipeline** — find in one list, validate result exists in another:

```
python deletion_theme.py --pattern RA --find "C:\Users\Stephen\Downloads\spreadthewordlist_caps.dict" --min-score 50 | python deletion_theme.py --pattern RA --validate - example_dictionary.txt --show-deletion-result
```

Candidates come from the scored `.dict`; deletion results are checked against the plain-text list.

---

## Useful Filters

| Flag | What it does |
|------|-------------|
| `--valid-only` | Drop words with no valid deletion (no output noise) |
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
