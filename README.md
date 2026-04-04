# Notion Export Prettify GUI

A desktop GUI wrapper for the [`notion-export-prettify`](https://github.com/nicholasgmm/notion-export-prettify) CLI tool. Point it at a Notion export (ZIP or HTML), fill in a few metadata fields, toggle some options, and generate a styled PDF — all without touching the command line.

## Features

- **Automatic ZIP handling** — accepts the outer ZIP downloaded directly from Notion and automatically extracts the inner `Export-*.zip` before passing it to the CLI
- **Document metadata** — set title, subtitle, description, project, author, date, and identifier
- **Tri-state option switches** — each boolean CLI flag can be explicitly enabled, disabled, or left at its default (omitted), giving full control without overriding CLI defaults unintentionally
- **Live output log** — streams CLI stdout/stderr in real time so you can see exactly what the tool is doing
- **Cancellable runs** — a Cancel button terminates the subprocess at any point
- **System theme** — adapts to your OS light/dark preference via CustomTkinter

## Prerequisites

| Requirement | Details |
|---|---|
| Python | ≥ 3.14 |
| `notion-export-prettify` | Must be installed and on your `PATH` |
| `uv` (recommended) | For managing the virtual environment and dependencies |

Install the CLI tool first. Refer to the [notion-export-prettify documentation](https://github.com/nicholasgmm/notion-export-prettify) for installation instructions.

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd notion-prettify

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Usage

### Launch the GUI

```bash
# With uv
uv run notion-prettify-gui

# Or directly
python main.py
```

### Workflow

1. **Files section** — select your Notion export (`.zip` or `.html`), optionally choose an output PDF path, and optionally provide a custom template/config file.
2. **Metadata section** — fill in any document metadata fields you want embedded in the PDF (all optional).
3. **Options section** — toggle the four boolean flags. Each switch cycles through three states:
   - **default** — flag is omitted (CLI default applies)
   - **on** — passes `--flag`
   - **off** — passes `--no-flag`
4. Click **Generate PDF** and monitor progress in the Output log.

### Options reference

| Option | CLI flag | Description |
|---|---|---|
| Cover page | `--cover-page` / `--no-cover-page` | Add a cover page if defined in the template |
| Heading numbers | `--heading-numbers` / `--no-heading-numbers` | Prefix headings with hierarchical numbers |
| Strip internal info | `--strip-internal-info` / `--no-strip-internal-info` | Remove callouts and database properties from output |
| Table of contents | `--table-of-contents` / `--no-table-of-contents` | Add a table of contents if present in the Notion export |

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Lint
uv run ruff check src

# Type-check
uv run mypy src

# Run tests
uv run pytest
```

## Project structure

```
src/notion_prettify_gui/
├── app.py                  # Main application window
├── models/
│   └── options.py          # PrettifyOptions dataclass + CLI arg builder
├── services/
│   ├── runner.py           # Subprocess management (background thread)
│   └── zip_handler.py      # Notion outer-ZIP extraction
└── widgets/
    ├── file_section.py     # Input / output / template file pickers
    ├── metadata_section.py # Document metadata fields
    └── options_section.py  # Tri-state boolean toggles
```
