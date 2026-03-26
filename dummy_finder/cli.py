from __future__ import annotations

import argparse
import json

from .ingest import ingest_directory, ingest_file, ingest_text
from .search import format_results, search


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dummy-finder")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_file_parser = subparsers.add_parser("ingest-file")
    ingest_file_parser.add_argument("path")
    ingest_file_parser.add_argument("--source", default="manual")
    ingest_file_parser.add_argument("--description", default="")
    ingest_file_parser.add_argument("--force", action="store_true")

    ingest_dir_parser = subparsers.add_parser("ingest-dir")
    ingest_dir_parser.add_argument("path")
    ingest_dir_parser.add_argument("--source", default="manual")
    ingest_dir_parser.add_argument("--recursive", action="store_true")
    ingest_dir_parser.add_argument("--force", action="store_true")

    ingest_text_parser = subparsers.add_parser("ingest-text")
    ingest_text_parser.add_argument("text")
    ingest_text_parser.add_argument("--title", default="text")
    ingest_text_parser.add_argument("--source", default="manual")
    ingest_text_parser.add_argument("--description", default="")
    ingest_text_parser.add_argument("--tags", default="")
    ingest_text_parser.add_argument("--force", action="store_true")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=5)
    search_parser.add_argument("--media-type", default=None)
    search_parser.add_argument("--json", action="store_true")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "ingest-file":
        result = ingest_file(
            args.path,
            source=args.source,
            description=args.description,
            force=args.force,
        )
        print(json.dumps(result, indent=2))
        return

    if args.command == "ingest-dir":
        result = ingest_directory(
            args.path,
            source=args.source,
            recursive=args.recursive,
            force=args.force,
        )
        print(json.dumps(result, indent=2))
        return

    if args.command == "ingest-text":
        result = ingest_text(
            args.text,
            title=args.title,
            source=args.source,
            description=args.description,
            tags=args.tags,
            force=args.force,
        )
        print(json.dumps(result, indent=2))
        return

    if args.command == "search":
        results = search(args.query, n_results=args.limit, media_type=args.media_type)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(format_results(results))
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
