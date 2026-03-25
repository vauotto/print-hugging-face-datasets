import argparse

from dataset_printer.constants import DEFAULT_DATASET


def build_parser():
    """Construct the CLI argument parser (no parsing)."""
    parser = argparse.ArgumentParser(
        description=(
            "Load a Hugging Face dataset and print rows "
            "(full JSON per line, or selected column(s) with --field / --auto-text-field)."
        ),
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        default=DEFAULT_DATASET,
        help=f"Dataset repo id (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="NAME",
        help="Dataset configuration / subset name (e.g. default)",
    )
    parser.add_argument(
        "--split",
        default=None,
        metavar="SPLIT",
        help="If set, only load and print this split",
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Stream rows without loading the full split into memory",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Allow running dataset scripts from the Hub (use only when required)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        metavar="N",
        help="Print at most N rows per split (debug / smoke test)",
    )
    parser.add_argument(
        "--field",
        action="append",
        default=None,
        metavar="NAME",
        help=(
            "Column to print; repeat for multiple columns. Order is preserved. "
            "With --plain-text, emits one text line per column per dataset row (row-major). "
            "Without --plain-text, one field is a JSON value per line; two or more fields "
            "produce one JSON object per line with those keys."
        ),
    )
    parser.add_argument(
        "--plain-text",
        action="store_true",
        help=(
            "Print field values as raw text: one line per column per dataset row "
            "(row-major when multiple --field)."
        ),
    )
    parser.add_argument(
        "--no-split-headers",
        action="store_true",
        help="Do not print '=== split: ... ===' lines (for pipelines)",
    )
    parser.add_argument(
        "--auto-text-field",
        action="store_true",
        help=(
            "Pick a string column automatically (preference list + first non-blocklisted "
            "str column). May be wrong on ambiguous schemas."
        ),
    )
    parser.add_argument(
        "--label",
        type=int,
        default=None,
        metavar="N",
        help="If set, only print rows where the 'label' column equals N",
    )
    return parser


def parse_args(argv=None):
    """Parse argv and apply cross-flag validation."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.explicit_fields = tuple(args.field) if args.field else None
    if args.plain_text and args.explicit_fields is None and not args.auto_text_field:
        parser.error("--plain-text requires --field or --auto-text-field")
    return args
