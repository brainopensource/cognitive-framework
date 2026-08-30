"""Installable LDA facade."""
from importlib import import_module

__version__ = "0.2.0"

def engine():
    return import_module("tools.007_LLM_DOCS_ATLAS")
