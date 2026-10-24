"""
Build-time patch for Music Assistant's bundled translations/en.json.

Upstream MA ships a pre-baked ``translations/en.json`` built by a repo-only
``scripts/build_translations.py`` that walks each provider's ``strings.json``.
That script is not in the installed package, so dropping a ``strings.json``
into our provider directory at image build time does nothing on its own —
at runtime MA reads ``en.json`` only.

This script merges our providers' ``strings.json`` into the bundled
``en.json`` so our ``manifest.name`` and ``manifest.description`` are
visible in the UI, and (importantly for the Mixtape provider) override
upstream's ``provider.spotify.manifest.description`` which would otherwise
win against our ``manifest.json``.

The key shape MA uses is ``<owner>.<domain>.<path>`` where ``<owner>`` is
``provider`` for sideloaded providers, and ``<path>`` is dot-joined keys
from the ``strings.json`` tree (e.g. ``manifest.description``).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import music_assistant  # resolves the real site-packages path

PKG_DIR = Path(music_assistant.__file__).resolve().parent
EN_JSON = PKG_DIR / "translations" / "en.json"


def _flatten(prefix: str, obj: object, out: dict[str, str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flatten(f"{prefix}.{k}" if prefix else k, v, out)
    elif isinstance(obj, str):
        out[prefix] = obj


def main() -> int:
    if not EN_JSON.exists():
        print(f"patch_translations: {EN_JSON} missing", file=sys.stderr)
        return 1

    with EN_JSON.open(encoding="utf-8") as f:
        catalogue: dict[str, str] = json.load(f)

    changed = 0
    for provider_dir in sorted((PKG_DIR / "providers").iterdir()):
        if provider_dir.name not in {"ytmusic_anon", "spotify"}:
            continue
        strings_path = provider_dir / "strings.json"
        if not strings_path.exists():
            continue
        with strings_path.open(encoding="utf-8") as f:
            strings = json.load(f)
        flat: dict[str, str] = {}
        _flatten("", strings, flat)
        for subkey, value in flat.items():
            full_key = f"provider.{provider_dir.name}.{subkey}"
            if catalogue.get(full_key) != value:
                catalogue[full_key] = value
                changed += 1
                print(f"patch_translations: set {full_key}")

    if changed:
        with EN_JSON.open("w", encoding="utf-8") as f:
            json.dump(catalogue, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"patch_translations: updated {changed} keys in {EN_JSON}")
    else:
        print("patch_translations: no changes needed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
