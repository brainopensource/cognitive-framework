# syntax=docker/dockerfile:1.4
# Immutable exterior evaluator container definition (S6B-REL-003, S6B-MD-007)
# Identity: unprivileged evaluator user (UID 10002:GID 10002)
# Sealed oracle directory mounted read-only; no network; no writable host paths

FROM alpine:3.19.1

RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-cryptography \
    git \
    coreutils \
    bash \
    shadow \
    && addgroup -g 10002 vgeval \
    && adduser -u 10002 -G vgeval -s /bin/sh -D vgeval \
    && mkdir -p /sealed-oracle /workspace /run/evaluator \
    && chown -R 10002:10002 /run/evaluator \
    && rm -rf /var/cache/apk/*

COPY pyproject.toml README.md /opt/vanguard/
COPY vanguard /opt/vanguard/vanguard
RUN python3 -m pip install --break-system-packages --no-cache-dir --no-deps /opt/vanguard

USER 10002:10002
WORKDIR /workspace
ENV PATH="/usr/bin:/bin"
ENV HOME="/tmp"

# Evaluator daemon runs over Unix socket in /run/evaluator/eval.sock
ENTRYPOINT ["/usr/bin/python3", "-m", "vanguard.packages.adapters.evaluators.daemon"]
CMD ["--socket", "/run/evaluator/eval.sock", "--workspace", "/workspace", "--oracle-manifest", "/sealed-oracle/preregistered_oracles.json", "--image-digest", "sha256:0ab368dd2071f556bf6987583ec210855341aab148b9100055d4cf37f2d34b89", "--command", "python3", "-m", "pytest", "-q"]
