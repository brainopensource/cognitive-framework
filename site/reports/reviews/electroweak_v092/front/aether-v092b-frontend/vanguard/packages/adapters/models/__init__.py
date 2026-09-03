"""Model adapter family; sibling adapter families must not import this package.

PEP 562 lazy attribute access. `ollama` pulls urllib -> http.client ->
email.parser (~106ms) which a `local`/fake-model run never uses. Names stay
importable; the module body is only executed on first attribute access.
"""
from typing import TYPE_CHECKING

_LAZY = {
    "Cassette": ".cassette", "CassettePlayer": ".cassette",
    "CassetteRecord": ".cassette", "CassetteRecorder": ".cassette",
    "FakeModel": ".fake",
    "ModelInvocation": ".invocation", "ProposalTranslator": ".invocation",
    "LamModelAdapter": ".lam",
    "OllamaModel": ".ollama",
    "StochasticModelAdapter": ".stochastic",
    "perturbation_key": ".stochastic",
    "RECOVERABLE_BLOCK_TYPES": ".stochastic",
    "get_default_model": ".config",
    "get_default_paid_model": ".config",
    "get_free_model": ".config",
    "get_medium_model": ".config",
    "get_high_model": ".config",
    "get_testing_model": ".config",
    "get_band_models": ".config",
    "get_pricing_micros_table": ".config",
    "get_pricing_usd_table": ".config",
    "load_model_registry": ".config",
    "create_model": ".factory",
    "ModelResolutionError": ".factory",
}

def __getattr__(name):
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module
    value = getattr(import_module(module, __name__), name)
    globals()[name] = value          # cache: subsequent access is a dict hit
    return value

def __dir__():
    return sorted(_LAZY)

if TYPE_CHECKING:                    # keep static analysis and IDEs working
    from .cassette import Cassette, CassettePlayer, CassetteRecord, CassetteRecorder
    from .fake import FakeModel
    from .invocation import ModelInvocation, ProposalTranslator
    from .lam import LamModelAdapter
    from .ollama import OllamaModel
    from .stochastic import RECOVERABLE_BLOCK_TYPES, StochasticModelAdapter, perturbation_key
    from .factory import ModelResolutionError, create_model


__all__ = list(_LAZY)
