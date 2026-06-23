# markitdown-he-patch

Hebrew/RTL fixes for [microsoft/markitdown](https://github.com/microsoft/markitdown), packaged as a drop-in patch.

## What's fixed

- **PDF**: Hebrew (and other RTL) text was coming out reversed and fragmented
  into one-word-per-line garbage for PDFs with no form-style pages. Root
  cause: the converter discarded correctly-extracted text and re-extracted
  the whole document with `pdfminer`, which mangles RTL layout. Fixed by
  detecting RTL-dominant text and keeping the already-correct extraction.
- **CSV**: a UTF-8 BOM character was leaking into the first cell's content.
  Common with CSVs exported from Excel containing Hebrew/non-ASCII text,
  since Excel prepends a BOM to mark the file as UTF-8.

## Install

Requires Python 3.10+.

```bash
python install.py
```

This will:
1. Install `markitdown[all]` from PyPI if it isn't already installed.
2. Back up the two affected files (`*.orig`) inside your markitdown
   installation.
3. Overwrite them with the patched versions in this folder.

## Uninstall

```bash
python install.py --uninstall
```

Restores the original files from the `.orig` backups.

## Verify

```bash
python -c "from markitdown import MarkItDown; print(MarkItDown().convert('your_hebrew_file.pdf').markdown)"
```

## Claude Code skill: /markitdown_he

`skills/markitdown_he/SKILL.md` adds a `/markitdown_he` slash command for
Claude Code that batch-converts every file in a folder you choose.

To enable it in a project, copy the skill folder into that project's
`.claude/skills/`:

```bash
mkdir -p .claude/skills
cp -r markitdown-he-patch/skills/markitdown_he .claude/skills/
```

Then run `/markitdown_he` in Claude Code. First run: paste the folder path
when asked — it's remembered for next time. Every supported file in that
folder gets converted to a `.md` file alongside it.
