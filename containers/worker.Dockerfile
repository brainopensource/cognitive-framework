# syntax=docker/dockerfile:1.4
# Immutable rootless worker container definition (S6B-REL-003, S6B-MD-006)
# Identity: unprivileged worker user (UID 10001:GID 10001)
# No root capabilities, no host sockets, sanitized PATH

FROM alpine:3.19.1

RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-cryptography \
    git \
    patch \
    grep \
    coreutils \
    bash \
    bubblewrap \
    shadow \
    && addgroup -g 10001 vgworker \
    && adduser -u 10001 -G vgworker -s /bin/sh -D vgworker \
    && rm -rf /var/cache/apk/*

COPY pyproject.toml README.md /opt/vanguard/
COPY vanguard /opt/vanguard/vanguard
RUN python3 -m pip install --no-cache-dir --no-deps /opt/vanguard

USER 10001:10001
WORKDIR /workspace
ENV PATH="/usr/bin:/bin"
ENV HOME="/tmp"

ENTRYPOINT ["/usr/bin/bwrap"]
