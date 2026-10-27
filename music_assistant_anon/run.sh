#!/bin/sh
# Install/refresh the three custom providers this add-on opinionates on, into
# the custom_providers directory the fork's mechanism scans at startup.
#
# Fail soft: a network outage or a 404 keeps the existing dir in place and
# never blocks Music Assistant from starting. The fork image is upstream
# Music Assistant plus the custom-providers loader; this script is what makes
# "the Boombox + Mixtape + JW.org Music add-on" different from "the generic
# fork image."
set -eu

CUSTOM_PROVIDERS_DIR=/data/custom_providers
mkdir -p "$CUSTOM_PROVIDERS_DIR"

# repo:provider_domain:branch_or_tag
# Pin a specific tag per repo if you want reproducible installs.
PROVIDERS="
music-assistant-boombox:ytmusic_anon:main
music-assistant-mixtape:spotify:main
music-assistant-jwmusic:jwmusic:main
"

for entry in $PROVIDERS; do
    [ -z "$entry" ] && continue
    repo="${entry%%:*}"
    rest="${entry#*:}"
    dir="${rest%%:*}"
    ref="${rest#*:}"

    tmp="$(mktemp -d)"
    url="https://github.com/jgruber/${repo}/archive/refs/heads/${ref}.tar.gz"
    # A tag reference lives under refs/tags/<tag>.tar.gz
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
            echo "[addon-run]   WARN: ${repo} archive did not contain expected directory '${dir}' — keeping any existing copy"
        fi
    else
        echo "[addon-run]   WARN: fetch failed for ${url} — keeping any existing copy"
    fi
    rm -rf "$tmp"
done

# Chain to the base image's entrypoint. The fork image sets LD_PRELOAD for
# jemalloc, then execs mass with the args we pass through here (CMD).
exec /usr/local/bin/entrypoint.sh "$@"
