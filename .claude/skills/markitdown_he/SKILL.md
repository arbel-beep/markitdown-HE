---
name: markitdown_he
description: Use when the user invokes /markitdown_he, or asks to batch-convert a folder of Hebrew documents to Markdown. Converts every supported file in a remembered (or newly provided) folder to .md using the Hebrew/RTL-patched markitdown converters.
---

# markitdown_he

Batch-converts files in a user-chosen folder to Markdown using `markitdown`
(with the Hebrew/RTL PDF and CSV fixes from this patch applied). Remembers
the folder across sessions via project memory, so the user only has to give
the path once.

## Step 1 — Resolve the target folder

Check project memory for an existing `markitdown-he-source-folder` memory
(type: project) recording a previously-confirmed folder path.

- **If found:** verify the folder still exists (`Read`/`Bash` a quick
  existence check). If it exists, use it directly — do not ask the user
  again. If it no longer exists, fall through to "not found" below.
- **If not found (or stale):** ask the user, in chat, to paste the full
  path to the folder containing the files to convert. Wait for their
  reply — do not guess or invent a path.

Once you have a confirmed, existing path, save/update it as a project
memory (per the memory system: write the memory file with frontmatter
`type: project`, then add a one-line pointer to `MEMORY.md`). Record the
absolute path and the date confirmed.

## Step 2 — Verify the patch is installed

Before converting, confirm the Hebrew/RTL patch is active in the user's
`markitdown` install:

```bash
python -c "from markitdown.converters._pdf_converter import _is_rtl_dominant"
```

If this raises `ImportError`, the stock (unpatched) `markitdown` is
installed. Tell the user, and offer to run `install.py` from this same
`markitdown-he-patch` folder before continuing.

## Step 3 — Convert every file in the folder

For each file directly inside the target folder (non-recursive unless the
user asks otherwise):

1. Skip files already ending in `.md`, and skip any `.md` file that already
   exists for a given source file (e.g. skip converting `report.pdf` if
   `report.md` is newer than `report.pdf`) — don't reconvert unchanged work.
2. Convert with `MarkItDown().convert(path)`.
3. Write the result next to the source file, same basename, `.md`
   extension, UTF-8 encoded (Windows consoles can't print Hebrew directly —
   always write to a file, never rely on printing the content to the
   terminal).
4. Track per-file success/failure.

## Step 4 — Report results

Give the user a short summary: how many files converted, where the `.md`
files were written, and call out any failures with the actual error
message (not a guess). Don't dump full Hebrew content into the chat unless
asked — just confirm files were written and where.
