import argparse
import sys

from pydantic import ValidationError
from rich.console import Console

from .schema import Track, View, Viewconf, schema_json

console = Console()


def export(args: argparse.Namespace) -> None:
    print(schema_json(indent=args.indent))


def check(args: argparse.Namespace) -> None:
    try:
        if args.path == "-":
            raw = "\n".join(sys.stdin.readlines())
            Viewconf[View[Track]].model_validate_json(raw)
        else:
            with open(args.path) as file:
                raw = file.read()
            Viewconf[View[Track]].model_validate_json(raw)
        console.print("✅ valid viewconf.", style="green")
    except ValidationError:
        msg = "❌ Invalid viewconf."
        if args.verbose:
            console.print(msg, style="yellow")
            console.print_exception()

        console.print(
            f"{msg} Run [white]`higlass-schema check --verbose`[/white] for "
            "more details.",
            style="yellow",
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # export
    parser_export = subparsers.add_parser("export")
    parser_export.add_argument("--indent", type=int)
    parser_export.set_defaults(func=export)

    # check
    parser_check = subparsers.add_parser("check")
    parser_check.add_argument("path")
    parser_check.add_argument("--verbose", action="store_true")
    parser_check.set_defaults(func=check)

    ns = parser.parse_args(sys.argv[1:])
    ns.func(ns)
