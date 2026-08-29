"""Protocol middleware package."""

from .dsml_decoder import decode_dsml_markup
from .json_argument_normalizer import normalize_json_arguments
from .markdown_patch_detector import MarkdownPatchDetection, detect_markdown_patch
from .native_tool_call_decoder import decode_native_tool_call
from .role_history_validator import validate_role_history
from .tool_schema_validator import validate_tool_arguments
from .truncation_detector import detect_truncation

__all__ = [
    "decode_native_tool_call",
    "decode_dsml_markup",
    "normalize_json_arguments",
    "detect_markdown_patch",
    "MarkdownPatchDetection",
    "detect_truncation",
    "validate_tool_arguments",
    "validate_role_history",
]
