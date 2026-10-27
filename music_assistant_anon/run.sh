#!/bin/sh
# Install/refresh the Custom Provider Installer plugin into the fork's
# custom_providers directory, then hand off to Music Assistant.
#
# This add-on's whole job is to deliver the fork image with the installer
# plugin pre-staged. Operators pick any additional custom providers they
# want through the installer plugin's config UI once Music Assistant is
# up — the add-on takes no position on which providers to install.
#
# Fail soft: a network outage keeps the existing plugin dir in place and
# never blocks Music Assistant from starting.
set -eu

CUSTOM_PROVIDERS_DIR=/data/custom_providers
VENV=/app/venv
UV="$VENV/bin/uv"
mkdir -p "$CUSTOM_PROVIDERS_DIR"

# repo:provider_domain:branch_or_tag
# Only the installer plugin is bootstrapped here; everything else is the
# operator's choice through the installer's UI.
PROVIDERS="
music-assistant-provider-installer:provider_installer:main
"

# ---------- 1. Sync bootstrap plugin(s) ----------

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

# ---------- 2. Install EVERY custom provider's manifest requirements ----------
#
# The MA venv (/app/venv) lives in the container's writable layer, so it is
# wiped on every Supervisor rebuild/restart. The installer plugin pip-installs
# its own fetches, but that runs during MA's plugin init — after MA has
# already walked and imported the music/metadata/player providers. A provider
# that needs a non-stdlib dep (spotapi, ytmusicapi, …) will ModuleNotFoundError
# on the first boot after any container restart.
#
# Fix: before MA starts, walk every /data/custom_providers/*/manifest.json and
# install the union of their 'requirements' into /app/venv. The installer
# plugin's own pip-install stays as a safety net (and the authoritative one
# when a provider gets added mid-session).

REQS="$(mktemp)"
: >"$REQS"
if [ -x "$UV" ]; then
    for manifest in "$CUSTOM_PROVIDERS_DIR"/*/manifest.json; do
        [ -f "$manifest" ] || continue
        "$VENV/bin/python3" -c "
import json
with open('$manifest') as f:
    m = json.load(f)
for r in m.get('requirements', []) or []:
    print(r)
" >>"$REQS" || true
    done
    awk '!seen[$0]++' "$REQS" >"${REQS}.dedup" && mv "${REQS}.dedup" "$REQS"
    if [ -s "$REQS" ]; then
        echo "[addon-run] installing custom-provider requirements:"
        sed 's/^/[addon-run]   /' "$REQS"
        if ! "$UV" pip install --python "$VENV/bin/python3" --quiet -r "$REQS"; then
            echo "[addon-run] WARN: uv pip install failed"
        fi
    fi
else
    echo "[addon-run] WARN: $UV not found; cannot install custom-provider requirements"
fi
rm -f "$REQS"

# ---------- 3. Chain to the fork image's entrypoint ----------
exec /usr/local/bin/entrypoint.sh "$@"
