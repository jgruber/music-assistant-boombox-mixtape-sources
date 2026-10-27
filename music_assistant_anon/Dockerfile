ARG BUILD_FROM
FROM ${BUILD_FROM}

# The base image is ghcr.io/jgruber/music-assistant-server — upstream Music
# Assistant plus a HACS-style custom-providers loader. This add-on's only
# job is to pre-stage the Custom Provider Installer plugin into
# /data/custom_providers/ on every start, so the operator can install any
# custom providers they want through the plugin's config UI once MA is up.
# The add-on takes no position on which specific providers to install.

COPY run.sh /usr/local/bin/addon-run.sh
RUN chmod +x /usr/local/bin/addon-run.sh

# Replace the base entrypoint so our run.sh runs first and then chains to it.
# The CMD stays what the base image used: --data-dir /data --cache-dir /data/.cache.
ENTRYPOINT ["/usr/local/bin/addon-run.sh"]
CMD ["--data-dir", "/data", "--cache-dir", "/data/.cache"]

LABEL \
  io.hass.name="Music Assistant Server (jgruber fork)" \
  io.hass.description="jgruber/music-assistant-server fork pre-staged with the Custom Provider Installer plugin" \
  io.hass.type="addon" \
  io.hass.version="2.10.8-fork.6"
