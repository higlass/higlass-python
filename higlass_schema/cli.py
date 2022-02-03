import argparse
import sys

from .schema import schema_json, Viewconf, View, Track

from pydantic import ValidationError

from rich.console import Console

console = Console()


def export(_: argparse.Namespace) -> None:
    console.print_json(schema_json(indent=2))


def check(args: argparse.Namespace) -> None:
    try:
        if args.path == "-":
            raw = "\n".join(sys.stdin.readlines())
            Viewconf[View[Track]].parse_raw(raw)
        else:
            Viewconf[View[Track]].parse_file(args.path)
        console.print("✅ Valid viewconf.", style="green")
    except ValidationError:
        if args.verbose:
            console.print("❌ invalid viewconf.", style="yellow")
            console.print_exception()
        else:
            console.print(
                "❌ Invalid viewconf. Run [white]`hgschema check --verbose`[/white] for more details.",
                style="yellow",
            )


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # export
    parser_export = subparsers.add_parser("export")
    parser_export.set_defaults(func=export)

    # check
    parser_check = subparsers.add_parser("check")
    parser_check.add_argument("path")
    parser_check.add_argument("--verbose", action="store_true")
    parser_check.set_defaults(func=check)

    ns = parser.parse_args(sys.argv[1:])
    ns.func(ns)
