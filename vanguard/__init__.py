"""Vanguard implementation root. Physical packages only; see packages/README.md."""

from importlib.metadata import PackageNotFoundError, version


try:
    # Keep the installed distribution metadata as the version authority.  The
    # fallback is intentionally the package's declared development version so
    # source checkouts and an installed wheel expose the same public value.
    __version__ = version("vanguard-runtime")
except PackageNotFoundError:  # pragma: no cover - source tree without metadata
    __version__ = "0.7.3.dev0"


__all__ = ["__version__"]
