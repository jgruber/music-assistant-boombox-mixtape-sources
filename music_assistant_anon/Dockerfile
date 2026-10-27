ARG BUILD_FROM
FROM ${BUILD_FROM}

# The base image is ghcr.io/jgruber/music-assistant-server, which is upstream
# Music Assistant plus a HACS-style custom-providers loader. This add-on's
# only job is to pre-populate /data/custom_providers/ with the three
# providers it ships with (Boombox, Mixtape, JW.org Music) on every start,
# so a fresh install (empty /data) still gets them, and existing installs
# auto-update to the latest release of each.

COPY run.sh /usr/local/bin/addon-run.sh
RUN chmod +x /usr/local/bin/addon-run.sh

# Replace the base entrypoint so our run.sh runs first and then chains to it.
# The CMD stays what the base image used: --data-dir /data --cache-dir /data/.cache.
ENTRYPOINT ["/usr/local/bin/addon-run.sh"]
CMD ["--data-dir", "/data", "--cache-dir", "/data/.cache"]

LABEL \
  io.hass.name="Music Assistant (Boombox + Mixtape + JW.org Music)" \
  io.hass.description="Music Assistant with Boombox, Mixtape and JW.org Music auto-installed as custom providers" \
  io.hass.type="addon" \
  io.hass.version="2.10.8-fork.2"
