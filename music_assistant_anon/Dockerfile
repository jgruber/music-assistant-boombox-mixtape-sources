ARG BUILD_FROM
FROM ${BUILD_FROM}

# The upstream MA image puts its venv at /app/venv/ and uses `uv` as its package manager
# (no pip in the venv). MA does not auto-install a sideloaded provider's manifest
# `requirements`, so we bake them in here. Pin `ytmusicapi` to the version the official
# ytmusic provider pins so both providers see the same ytmusicapi behavior; `yt-dlp` is
# the only true additional dep for ytmusic_anon.
RUN set -eux; \
    VENV_PY=/app/venv/bin/python3; \
    /app/venv/bin/uv pip install --python "$VENV_PY" \
        "ytmusicapi==1.12.3" \
        "yt-dlp>=2025.09.26" \
        "bgutil-ytdlp-pot-provider==2.0.1" \
        "deno==2.9.5" \
        "spotapi" "redis" "websockets" "pymongo"; \
    "$VENV_PY" -c "import ytmusicapi, yt_dlp, spotapi, deno; print('baked:', ytmusicapi.__version__, yt_dlp.version.__version__)"; \
    # deno is a Python wrapper that drops a `deno` binary into the venv on first use;
    # trigger it now so the binary is ready at container start and yt-dlp can find it
    # on PATH for signature deciphering.
    /app/venv/bin/python3 -c "import deno; deno.install()" 2>/dev/null || true; \
    ls -la /app/venv/bin/deno 2>&1 || echo "deno binary not pre-staged (will be fetched on first use)"

# Resolve the installed music_assistant package's providers directory at build time
# (rather than hardcoding /app/venv/lib/python3.X/) so a Python-version bump upstream
# doesn't silently break us.
COPY ytmusic_anon /tmp/ytmusic_anon
COPY spotify /tmp/spotify
RUN set -eux; \
    PROVIDERS_DIR="$(/app/venv/bin/python3 -c 'import music_assistant, os; print(os.path.dirname(music_assistant.__file__))')/providers"; \
    test -d "$PROVIDERS_DIR"; \
    # Our provider module declares domain="spotify" so MA's URL interception
    # routes open.spotify.com paste directly to it. The upstream stock Spotify
    # provider also claims that domain, so remove it to avoid a collision.
    # (This fork is for users without a Spotify Premium account, so the stock
    # provider wouldn't work anyway.)
    rm -rf "$PROVIDERS_DIR/spotify"; \
    cp -r /tmp/ytmusic_anon "$PROVIDERS_DIR/"; \
    cp -r /tmp/spotify "$PROVIDERS_DIR/"; \
    rm -rf /tmp/ytmusic_anon /tmp/spotify; \
    ls -la "$PROVIDERS_DIR/ytmusic_anon" "$PROVIDERS_DIR/spotify"

# Patch MA core: _search_shareable_url ignores the caller's media_types, so the
# UI's per-section search calls each receive the resolved item and the frontend
# shows a pasted Spotify URL 7-10 times. See patch_core.py for details.
COPY patch_core.py /tmp/patch_core.py
RUN /app/venv/bin/python3 /tmp/patch_core.py && rm /tmp/patch_core.py

# Patch MA translations: merge our providers' strings.json into the bundled
# translations/en.json so our provider name/description are visible in the UI
# (and override upstream's provider.spotify.manifest.description entry).
# See patch_translations.py for details.
COPY patch_translations.py /tmp/patch_translations.py
RUN /app/venv/bin/python3 /tmp/patch_translations.py && rm /tmp/patch_translations.py

LABEL \
  io.hass.name="Music Assistant (Boombox + Mixtape)" \
  io.hass.description="Music Assistant with the Boombox and Mixtape providers baked in" \
  io.hass.type="addon" \
  io.hass.version="2.10.8-boombox.3"
