#!/bin/sh
# Install/refresh the three custom providers this add-on opinionates on, into
# the custom_providers directory the fork's mechanism scans at startup, then
# install each one's manifest requirements into Music Assistant's venv.
#
# Fail soft: a network outage or a 404 keeps the existing dir in place and
# never blocks Music Assistant from starting. The fork image is upstream
# Music Assistant plus the custom-providers loader; this script is what makes
# "the Boombox + Mixtape + JW.org Music add-on" different from the generic
# fork image.
set -eu

CUSTOM_PROVIDERS_DIR=/data/custom_providers
VENV=/app/venv
UV="$VENV/bin/uv"
mkdir -p "$CUSTOM_PROVIDERS_DIR"

# repo:provider_domain:branch_or_tag
# Pin a specific tag per repo if you want reproducible installs.
PROVIDERS="
music-assistant-boombox:ytmusic_anon:main
music-assistant-mixtape:spotify:main
music-assistant-jwmusic:jwmusic:main
"

# ---------- 1. Sync provider sources ----------

for entry in $PROVIDERS; do
    [ -z "$entry" ] && continue
    repo="${entry%%:*}"
    rest="${entry#*:}"
    dir="${rest%%:*}"
    ref="${rest#*:}"

    tmp="$(mktemp -d)"
    url="https://github.com/jgruber/${repo}/archive/refs/heads/${ref}.tar.gz"
    case "$ref" in
        v*|[0-9]*)
            url="https://github.com/jgruber/${repo}/archive/refs/tags/${ref}.tar.gz"
            ;;
    esac
    echo "[addon-run] syncing ${repo}@${ref} -> ${CUSTOM_PROVIDERS_DIR}/${dir}"
    if wget -q -O - "$url" | tar -xzf - --strip-components=1 -C "$tmp" "${repo}-${ref#v}/${dir}" 2>/dev/null \
       || wget -q -O - "$url" | tar -xzf - --strip-components=1 -C "$tmp" "${repo}-${ref}/${dir}" 2>/dev/null; then
        if [ -d "$tmp/$dir" ]; then
            rm -rf "${CUSTOM_PROVIDERS_DIR:?}/${dir}"
            mv "$tmp/$dir" "${CUSTOM_PROVIDERS_DIR}/"
            echo "[addon-run]   ok"
        else
            echo "[addon-run]   WARN: ${repo} archive did not contain '${dir}' — keeping any existing copy"
        fi
    else
        echo "[addon-run]   WARN: fetch failed for ${url} — keeping any existing copy"
    fi
    rm -rf "$tmp"
done

# ---------- 2. Install each custom provider's manifest requirements ----------
#
# MA pip-installs a provider's requirements when the user adds it via the UI
# the first time, not on every start. For a fresh install (empty venv), or
# for a provider installed by this script (bypassing the UI flow), we have
# to install the requirements ourselves. Idempotent — uv reuses the resolved
# versions on subsequent runs.
#
# Collect requirements from every manifest, dedupe, then one uv pip install
# call so network cost is paid once per start.

REQS="$(mktemp)"
: >"$REQS"
if [ -x "$UV" ]; then
    for manifest in "$CUSTOM_PROVIDERS_DIR"/*/manifest.json; do
        [ -f "$manifest" ] || continue
        "$VENV/bin/python3" -c "
import json, sys
with open('$manifest') as f:
    m = json.load(f)
for r in m.get('requirements', []) or []:
    print(r)
" >>"$REQS" || true
    done
    # Dedupe while preserving order
    awk '!seen[$0]++' "$REQS" >"${REQS}.dedup" && mv "${REQS}.dedup" "$REQS"
    if [ -s "$REQS" ]; then
        echo "[addon-run] installing custom-provider requirements:"
        sed 's/^/[addon-run]   /' "$REQS"
        if ! "$UV" pip install --python "$VENV/bin/python3" --quiet -r "$REQS"; then
            echo "[addon-run] WARN: uv pip install failed — Music Assistant may skip providers whose deps are missing"
        fi
    else
        echo "[addon-run] no custom-provider requirements to install"
    fi
else
    echo "[addon-run] WARN: $UV not found; cannot install custom-provider requirements"
fi
rm -f "$REQS"

# ---------- 3. Chain to the fork image's entrypoint ----------
#
# The fork image sets LD_PRELOAD for jemalloc and then execs mass with the
# CMD args we pass through here.
exec /usr/local/bin/entrypoint.sh "$@"
