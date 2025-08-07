import sys
from pathlib import Path

# Ensure the package root is on the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from parse_amass import categorize_entry, parse_file


def test_categorize_entry():
    assert categorize_entry("192.168.0.1")[0] == "ips"
    assert categorize_entry("https://example.com")[0] == "urls"
    assert categorize_entry("www.example.com")[0] == "fqdns"


def test_parse_file(tmp_path):
    content = "\n".join([
        "192.168.1.1",
        "example.com",
        "https://sub.example.com/path",
    ])
    input_file = tmp_path / "amass.txt"
    input_file.write_text(content)
    categories = parse_file(str(input_file))
    assert categories["ips"] == ["192.168.1.1"]
    assert categories["fqdns"] == ["example.com"]
    assert categories["urls"] == ["https://sub.example.com/path"]
