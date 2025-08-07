import argparse
import ipaddress
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional


def categorize_entry(entry: str) -> Optional[Tuple[str, str]]:
    """Categorize a single line from amass output.

    Returns a tuple of (category, value) or None if the line is empty.
    Categories are "ips", "fqdns", and "urls".
    """
    line = entry.strip()
    if not line:
        return None

    # Check for IP address
    try:
        ipaddress.ip_address(line)
        return "ips", line
    except ValueError:
        pass

    # Check for URL
    parsed = urlparse(line)
    if parsed.scheme and parsed.netloc:
        return "urls", line

    # Treat everything else as FQDN
    return "fqdns", line


def parse_file(path: str) -> Dict[str, List[str]]:
    """Parse an amass output file into categorized lists."""
    categories: Dict[str, List[str]] = {"ips": [], "fqdns": [], "urls": []}
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            result = categorize_entry(line)
            if result is None:
                continue
            category, value = result
            categories[category].append(value)
    return categories


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse amass output into categories.")
    parser.add_argument("input", help="Path to the amass output file")
    parser.add_argument("--ips", help="File to write IP addresses to")
    parser.add_argument("--fqdns", help="File to write FQDNs to")
    parser.add_argument("--urls", help="File to write URLs to")
    args = parser.parse_args()

    categories = parse_file(args.input)

    if args.ips:
        with open(args.ips, "w", encoding="utf8") as f:
            f.write("\n".join(categories["ips"]))
    if args.fqdns:
        with open(args.fqdns, "w", encoding="utf8") as f:
            f.write("\n".join(categories["fqdns"]))
    if args.urls:
        with open(args.urls, "w", encoding="utf8") as f:
            f.write("\n".join(categories["urls"]))

    if not any([args.ips, args.fqdns, args.urls]):
        for key, values in categories.items():
            if not values:
                continue
            print(f"{key}:")
            for value in values:
                print(value)
            print()


if __name__ == "__main__":
    main()
