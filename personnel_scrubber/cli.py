"""Simple CLI for the personnel scrubber SQLite tracker."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from personnel_scrubber.tracker import RemovalRecord, connect, init_db, insert_removal, list_removals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="personnel-scrubber")
    parser.add_argument("--db", default="scrubber.db", help="SQLite database path (default: scrubber.db)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Create tracker tables")

    add_parser = subparsers.add_parser("add", help="Add a domain/listing tracking row")
    add_parser.add_argument("--domain", required=True)
    add_parser.add_argument("--listing-url", default="")
    add_parser.add_argument("--listing-found", action="store_true")
    add_parser.add_argument("--submitted", action="store_true")
    add_parser.add_argument("--awaiting-email", action="store_true")
    add_parser.add_argument("--verified", action="store_true")
    add_parser.add_argument("--recheck-date", default="", help="YYYY-MM-DD")
    add_parser.add_argument("--notes", default="")

    subparsers.add_parser("list", help="List tracked rows")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    db_path = Path(args.db)
    conn = connect(db_path)

    if args.command == "init-db":
        init_db(conn)
        print(f"Initialized database: {db_path}")
        return

    if args.command == "add":
        init_db(conn)
        recheck = date.fromisoformat(args.recheck_date) if args.recheck_date else None
        record = RemovalRecord(
            domain=args.domain,
            listing_url=args.listing_url,
            listing_found=args.listing_found,
            removal_submitted=args.submitted,
            awaiting_email_click=args.awaiting_email,
            verified=args.verified,
            recheck_date=recheck,
            notes=args.notes,
        )
        row_id = insert_removal(conn, record)
        print(f"Inserted record id={row_id} for domain={args.domain}")
        return

    if args.command == "list":
        init_db(conn)
        rows = list_removals(conn)
        if not rows:
            print("No records found.")
            return
        for row in rows:
            print(
                f"#{row['id']} {row['domain']} | found={row['listing_found']} submitted={row['removal_submitted']} "
                f"awaiting_email={row['awaiting_email_click']} verified={row['verified']} "
                f"recheck={row['recheck_date'] or '-'} listing={row['listing_url'] or '-'}"
            )
        return

    parser.error(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
