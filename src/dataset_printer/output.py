import json
from dataclasses import dataclass

from dataset_printer.constants import AUTO_FIELD_BLOCKLIST, AUTO_FIELD_PREFERENCES


class PrintDatasetError(Exception):
    """Raised for invalid user input or schema; message is shown on stderr."""


@dataclass(frozen=True)
class PrintConfig:
    """Options controlling how each row is filtered and serialized to stdout."""

    no_split_headers: bool
    explicit_field: str | None
    auto_text_field: bool
    plain_text: bool
    label_filter: int | None


class AutoTextFieldResolver:
    """Resolves the column name once when using --auto-text-field."""

    def __init__(self):
        self._column: str | None = None

    def column_for_row(self, row, explicit_field: str | None, use_auto: bool) -> str | None:
        """Return the field name to print for this row, or None for full-row JSON."""
        if explicit_field is not None:
            self._require_key(row, explicit_field, context="column")
            return explicit_field
        if use_auto:
            if self._column is None:
                self._column = pick_auto_text_field(row)
                if self._column is None:
                    raise PrintDatasetError(
                        "--auto-text-field found no suitable string column"
                    )
            self._require_key(row, self._column, context="auto-resolved column")
            return self._column
        return None

    def _require_key(self, row, key: str, context: str) -> None:
        if key not in row:
            keys = ", ".join(sorted(row.keys()))
            raise PrintDatasetError(
                f"{context} {key!r} not in row; available: {keys}"
            )


def pick_auto_text_field(row):
    """Choose a string column using preference order, then first non-blocklisted str."""
    for key in AUTO_FIELD_PREFERENCES:
        if key in row and isinstance(row[key], str):
            return key
    for key, val in row.items():
        if key not in AUTO_FIELD_BLOCKLIST and isinstance(val, str):
            return key
    return None


def row_matches_label_filter(row, label_filter: int | None) -> bool:
    """Return True if the row should be printed given optional --label."""
    if label_filter is None:
        return True
    if "label" not in row:
        raise PrintDatasetError("--label requires a 'label' column in the dataset")
    value = row["label"]
    try:
        return int(value) == label_filter
    except (TypeError, ValueError):
        return value == label_filter


def write_row_line(row, field_name: str | None, plain_text: bool) -> None:
    """Print one row: full JSON, JSON value of one field, or plain text for one field."""
    if field_name is None:
        print(json.dumps(row, ensure_ascii=False, default=str), flush=True)
        return
    value = row[field_name]
    if plain_text:
        line = value if isinstance(value, str) else str(value)
        print(line, flush=True)
    else:
        print(json.dumps(value, ensure_ascii=False, default=str), flush=True)


def write_split_header(split_name: str) -> None:
    """Print the human-readable split delimiter line."""
    print(f"=== split: {split_name} ===", flush=True)


def print_split_rows(
    split_name,
    rows,
    max_rows: int | None,
    config: PrintConfig,
    resolver: AutoTextFieldResolver,
) -> None:
    """Iterate rows in one split, apply filters, and print up to max_rows lines."""
    if not config.no_split_headers:
        write_split_header(split_name)
    printed = 0
    for row in rows:
        if not row_matches_label_filter(row, config.label_filter):
            continue
        field_name = resolver.column_for_row(
            row, config.explicit_field, config.auto_text_field
        )
        write_row_line(row, field_name, config.plain_text)
        printed += 1
        if max_rows is not None and printed >= max_rows:
            break
