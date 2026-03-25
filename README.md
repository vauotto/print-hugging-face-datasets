# Dataset Printer

Small command-line utility that loads a dataset from the [Hugging Face Hub](https://huggingface.co/datasets) using the `datasets` library and prints each row to **standard output**. By default it prints one JSON object per line; you can select one or more columns with repeated `--field`, export plain text (one line per column per dataset row when multiple fields are selected), and optionally filter by label.

Application code lives under [`src/dataset_printer/`](src/dataset_printer/). The [`print_dataset.py`](print_dataset.py) file at the repository root prepends `src` to `sys.path` and delegates to that package so you can keep running commands from the project root without installing the project.

## Requirements

- Python **3.10+** (the code uses modern type hints).
- Network access to `huggingface.co` when downloading or refreshing a dataset (unless it is already cached locally).

## Setup

From the project root:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with `env\Scripts\activate` instead of `source env/bin/activate`.

### Optional environment variables

If you use a `.env` file in the project directory, it is loaded automatically (`python-dotenv`). Typical variables:

| Variable | Purpose |
|----------|---------|
| `HF_TOKEN` | Hugging Face API token for higher rate limits and private datasets. |
| `HTTP_PROXY` / `HTTPS_PROXY` | Corporate HTTP(S) proxy. |
| `ALL_PROXY` | Avoid `socks://` here if you see `Unknown scheme for proxy URL` from `httpx`; prefer unsetting `ALL_PROXY` or using an `http://` proxy URL. |

## Where the data comes from

- The **dataset id** is the first positional argument (e.g. `deepset/prompt-injections` or `yanismiraoui/prompt_injections`). Data is fetched from the Hugging Face Hub via `datasets.load_dataset`.
- After the first download, the library caches files under your user cache (commonly `~/.cache/huggingface/datasets`). Later runs can use the cache offline if the revision is still available.

## Usage

Run from the project root (with the virtual environment activated):

```bash
python print_dataset.py [DATASET] [OPTIONS]
```

If you omit `DATASET`, the default is `deepset/prompt-injections`.

Equivalent module invocation (from the project root):

```bash
PYTHONPATH=src python -m dataset_printer [DATASET] [OPTIONS]
```

### Examples

```bash
python print_dataset.py
python print_dataset.py yanismiraoui/prompt_injections --split train
python print_dataset.py deepset/prompt-injections --field text --plain-text --no-split-headers > lines.txt
python print_dataset.py deepset/prompt-injections --field text --field label --plain-text --no-split-headers --max-rows 2
python print_dataset.py deepset/prompt-injections --field text --field label --no-split-headers --max-rows 2
python print_dataset.py deepset/prompt-injections --field text --label 1 --plain-text --no-split-headers
python print_dataset.py some/user/dataset --auto-text-field --plain-text --max-rows 10
python print_dataset.py some/user/dataset --streaming --split train
```

### Arguments

| Argument | Description |
|----------|-------------|
| `dataset` | Hugging Face dataset repo id (`owner/name`). Optional; defaults to `deepset/prompt-injections`. |
| `--config NAME` | Dataset configuration / subset name (when the repo defines multiple configs). |
| `--split SPLIT` | Load and print only this split (e.g. `train`). If omitted, all splits are printed with a header per split. |
| `--streaming` | Stream rows instead of loading the full split into memory. |
| `--trust-remote-code` | Allow the Hub to run dataset loading scripts from the repo (use only when you trust the source). |
| `--max-rows N` | Print at most `N` **dataset rows** per split after `--label` filtering (not counting extra lines when `--plain-text` prints multiple columns per row). |
| `--field NAME` | Select a column to print; pass the flag multiple times for multiple columns. Order is preserved. With `--plain-text`, prints one text line per column **per dataset row** (row-major: col₁, col₂, …, then next row). Without `--plain-text`: a single field yields one JSON-encoded **value** per line; two or more fields yield one JSON **object** per line containing only those keys. |
| `--plain-text` | Print selected field values as raw text. Requires `--field` or `--auto-text-field`. |
| `--no-split-headers` | Do not print `=== split: ... ===` lines (better for piping). |
| `--auto-text-field` | Guess a string column using a built-in preference list and fallbacks; can be wrong on ambiguous schemas. |
| `--label N` | Keep only rows whose `label` column equals integer `N`. |

For the full list and help text:

```bash
python print_dataset.py --help
```

## Disclaimer

This project and its documentation were produced **with assistance from artificial intelligence**. The code may contain bugs, omissions, or unsafe assumptions. **We do not warrant** correctness, fitness for any purpose, or the quality of third-party datasets accessed through the Hugging Face Hub. **We are not responsible** for the dataset contents, for how you use this script, or for any damages or losses arising from its use. Review the code and data policies before use in production or sensitive environments.
