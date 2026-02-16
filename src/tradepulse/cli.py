import argparse
import json
import sys

from tradepulse.pipeline.run_once import run_once


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tradepulse")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run one digest cycle")
    run_parser.add_argument("--dry-run", action="store_true", help="Do not push notifications")
    run_parser.add_argument("--json", action="store_true", help="Print result in JSON")

    args = parser.parse_args(argv)

    if args.command == "run":
        result = run_once(dry_run=args.dry_run)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["digest"])
            print("\n---")
            print(f"stats: {result['stats']}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
