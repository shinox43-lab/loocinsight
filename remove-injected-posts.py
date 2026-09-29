#!/usr/bin/env python3
"""Remove known injected WordPress post cards from a static HTML tree."""
import sys
from html.parser import HTMLParser
from pathlib import Path

INJECTED_POST_IDS = {"989189", "989190"}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class InjectedPostParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_offsets = [0]
        self.line_offsets.extend(
            index + 1 for index, char in enumerate(source) if char == "\n"
        )
        self.removal_start = None
        self.div_depth = 0
        self.ranges = []

    def source_offset(self, position):
        line, column = position
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if self.removal_start is not None:
            if tag == "div":
                self.div_depth += 1
            return

        if tag != "div":
            return

        classes = dict(attrs).get("class", "").split()
        if any(f"post-{post_id}" in classes for post_id in INJECTED_POST_IDS):
            self.removal_start = self.source_offset(self.getpos())
            self.div_depth = 1

    def handle_endtag(self, tag):
        if self.removal_start is None or tag != "div":
            return

        self.div_depth -= 1
        if self.div_depth == 0:
            start = self.source_offset(self.getpos())
            end = self.source.find(">", start)
            if end < 0:
                raise ValueError("Unterminated closing div tag")
            self.ranges.append((self.removal_start, end + 1))
            self.removal_start = None


def collect_removals(root):
    changes = []
    for path in sorted(root.rglob("*.html")):
        source = path.read_text(encoding="utf-8")
        parser = InjectedPostParser(source)
        parser.feed(source)
        parser.close()
        if parser.removal_start is not None:
            raise ValueError(f"Unclosed injected post card in {path}")
        if parser.ranges:
            changes.append((path, source, parser.ranges))
    return changes


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "site"
    if not root.is_dir():
        raise SystemExit(f"ERROR: HTML directory does not exist: {root}")

    changes = collect_removals(root)
    removed = 0
    for path, source, ranges in changes:
        for start, end in reversed(ranges):
            source = source[:start] + source[end:]
        path.write_text(source, encoding="utf-8")
        removed += len(ranges)

    print(f"Injected post cards removed: {removed} across {len(changes)} HTML files")


if __name__ == "__main__":
    main()
