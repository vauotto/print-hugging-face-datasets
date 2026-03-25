import sys

from dotenv import load_dotenv
from datasets import DatasetDict, load_dataset

from dataset_printer.cli import parse_args
from dataset_printer.output import (
    AutoTextFieldResolver,
    PrintConfig,
    PrintDatasetError,
    print_split_rows,
)

load_dotenv()


def load_dataset_kwargs(args):
    """Build keyword arguments for ``datasets.load_dataset`` from CLI args."""
    kwargs = {
        "streaming": args.streaming,
        "trust_remote_code": args.trust_remote_code,
    }
    if args.config is not None:
        kwargs["name"] = args.config
    if args.split is not None:
        kwargs["split"] = args.split
    return kwargs


def iter_splits(dataset, only_split: str | None):
    """Yield (split_label, split_data) for the loaded dataset object."""
    if only_split is not None:
        yield only_split, dataset
        return
    if isinstance(dataset, DatasetDict):
        yield from dataset.items()
        return
    yield "default", dataset


def print_config_from_args(args) -> PrintConfig:
    """Map argparse namespace to a frozen PrintConfig."""
    return PrintConfig(
        no_split_headers=args.no_split_headers,
        explicit_fields=args.explicit_fields,
        auto_text_field=args.auto_text_field,
        plain_text=args.plain_text,
        label_filter=args.label,
    )


def main():
    """Load the Hub dataset and print rows according to CLI options."""
    args = parse_args()
    try:
        dataset = load_dataset(args.dataset, **load_dataset_kwargs(args))
        config = print_config_from_args(args)
        resolver = AutoTextFieldResolver()
        for split_name, split_data in iter_splits(dataset, args.split):
            print_split_rows(
                split_name,
                split_data,
                args.max_rows,
                config,
                resolver,
            )
    except PrintDatasetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
