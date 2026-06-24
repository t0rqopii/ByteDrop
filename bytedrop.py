#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import sys
import zlib
from hashlib import sha256
from pathlib import Path

HEADER = "BYTEDROP-1"


class ByteDropError(Exception):
    pass


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def read_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise ByteDropError(f"File not found: {path}")
    return path.read_bytes()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def wrap(text: str, width: int = 76) -> str:
    return "\n".join(text[i:i + width] for i in range(0, len(text), width))


def make_payload(input_path: Path, compress: bool) -> str:
    raw = read_bytes(input_path)
    packed = zlib.compress(raw) if compress else raw
    data = base64.b64encode(packed).decode("ascii")
    meta = {
        "v": 1,
        "name": input_path.name,
        "size": len(raw),
        "sha256": digest(raw),
        "zlib": compress,
    }
    return "\n".join([HEADER, json.dumps(meta, separators=(",", ":")), wrap(data)]) + "\n"


def read_payload(path: Path) -> tuple[dict, bytes]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0].strip() != HEADER:
        raise ByteDropError("Invalid payload.")
    meta = json.loads(lines[1])
    blob = base64.b64decode("".join(lines[2:]), validate=True)
    raw = zlib.decompress(blob) if meta.get("zlib") else blob
    if len(raw) != int(meta["size"]):
        raise ByteDropError("Size mismatch.")
    if digest(raw) != meta["sha256"]:
        raise ByteDropError("Checksum mismatch.")
    return meta, raw


def cmd_encode(args: argparse.Namespace) -> int:
    out = args.output or args.input.with_name(f"{args.input.name}.bytedrop.txt")
    write_text(out, make_payload(args.input, args.compress))
    print(f"Payload written to {out}")
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    meta, raw = read_payload(args.input)
    out = args.output or Path(f"recovered_{meta['name']}")
    write_bytes(out, raw)
    print(f"Recovered file written to {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="bytedrop", description="Encode files into text and recover them later.")
    s = p.add_subparsers(dest="cmd", required=True)

    e = s.add_parser("encode", help="Encode a file into text.")
    e.add_argument("input", type=Path)
    e.add_argument("-o", "--output", type=Path)
    e.add_argument("--compress", action="store_true")
    e.set_defaults(func=cmd_encode)

    d = s.add_parser("decode", help="Decode text back into a file.")
    d.add_argument("input", type=Path)
    d.add_argument("-o", "--output", type=Path)
    d.set_defaults(func=cmd_decode)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except (ByteDropError, json.JSONDecodeError, base64.binascii.Error, zlib.error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
