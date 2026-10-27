ARG BUILD_FROM
FROM ${BUILD_FROM}

# The base image is now ghcr.io/jgruber/music-assistant-server, which bakes in the three
# providers (Boombox, Mixtape, JW.org Music), their runtime deps (yt-dlp, spotapi, bgutil,
# deno, etc.), the URL-search filter fix, CONF_PUBLISH_BASE_URL, and the HACS-style custom
# providers mechanism. No overlay patches needed here any more.

LABEL \
  io.hass.name="Music Assistant (Boombox + Mixtape + JW.org Music)" \
  io.hass.description="Music Assistant with the Boombox, Mixtape and JW.org Music providers baked in" \
  io.hass.type="addon" \
  io.hass.version="2.10.8-fork.1"
