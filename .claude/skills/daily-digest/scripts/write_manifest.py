"""
write_manifest.py — Write a sidecar manifest JSON file alongside a digest.

Usage:
    python write_manifest.py <digest_path> <manifest_json>

Arguments:
    digest_path   Path to the digest .md file (used to derive manifest path)
    manifest_json Complete manifest payload as a compact JSON string

Exit codes:
    0 — success
    1 — error (message printed to stderr)
"""

import json
import os
import sys


def derive_manifest_path(digest_path):
    if not digest_path.endswith(".md"):
        raise ValueError(f"digest_path must end with .md, got: {digest_path!r}")
    return digest_path[:-3] + ".manifest.json"


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: write_manifest.py <digest_path> <manifest_json>",
            file=sys.stderr,
        )
        sys.exit(1)

    digest_path = sys.argv[1]
    manifest_json_str = sys.argv[2]

    # Validate JSON
    try:
        payload = json.loads(manifest_json_str)
    except json.JSONDecodeError as exc:
        print(f"Error: manifest_json is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    # Derive manifest path
    try:
        manifest_path = derive_manifest_path(digest_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Create directories if needed
    manifest_dir = os.path.dirname(manifest_path)
    if manifest_dir:
        os.makedirs(manifest_dir, exist_ok=True)

    # Write manifest
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, indent=2, ensure_ascii=False))
            f.write("\n")
    except OSError as exc:
        print(f"Error writing manifest: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Manifest created: {manifest_path}")


if __name__ == "__main__":
    main()
