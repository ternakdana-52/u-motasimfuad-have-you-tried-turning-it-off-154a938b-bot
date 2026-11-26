#!/usr/bin/env python3
"""Write the tech-support one-liner to /output/entry.txt.

Entry for make.fun's "Have You Tried Turning It Off?" bounty: one
funny single-line reply from a hopeless tech support agent to a
desperate customer, 1 to 199 characters.

The line is fixed in this file. The program checks it before writing:
it must be one line, non-blank, valid UTF-8 and no longer than 199
characters. It then writes it to /output/entry.txt (or
$MAKEFUN_OUTPUT_DIR/entry.txt when that is set), keeps a review copy
as entry.txt beside this file, and reads the written file back to
confirm the bytes match. No network, no randomness, no state: two
runs produce byte-identical output.
"""

import hashlib
import os
import sys

MAX_CHARS = 199

LINE = (
    "Have you tried turning it off and on again? I already did, "
    "twice, from here, just by thinking about it really hard. "
    "Your turn."
)

HERE = os.path.dirname(os.path.abspath(__file__))


def fail(message):
    print(f"entry.txt rejected: {message}", file=sys.stderr)
    return 1


def check_line(line):
    if not line:
        return "empty line"
    if line != line.strip():
        return "leading or trailing whitespace"
    if "\n" in line or "\r" in line:
        return "more than one line"
    if any(ord(ch) < 0x20 for ch in line):
        return "control characters in line"
    if len(line) > MAX_CHARS:
        return f"{len(line)} characters, over the 199 cap"
    try:
        line.encode("utf-8")
    except UnicodeEncodeError:
        return "not valid UTF-8"
    if not line.strip():
        return "only whitespace"
    return None


def write_text(path, text):
    data = text.encode("utf-8")
    with open(path, "wb") as handle:
        handle.write(data)
    os.chmod(path, 0o644)
    return data


def main() -> int:
    problem = check_line(LINE)
    if problem is not None:
        return fail(problem)
    data = LINE.encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    write_text(target, LINE)
    with open(target, "rb") as handle:
        if hashlib.sha256(handle.read()).hexdigest() != digest:
            return fail("copy does not match the line")

    # Best-effort review copy beside this file; the grader mounts the
    # repo read-only, so a failed write here must not fail the run.
    try:
        write_text(os.path.join(HERE, "entry.txt"), LINE)
    except OSError:
        pass
    print(f"wrote {target} ({len(LINE)} chars, sha256 {digest[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
