from ..core.profile import RepositoryProfile

def profile() -> RepositoryProfile:
    return RepositoryProfile(
        name="AETHER", generated_root=".generated", cache_root=".generated/lda-cache",
        preferred_authority=("constitutional", "normative", "canonical"),
        secondary_authority=("descriptive", "reference"),
        excluded_authority=("non-canonical", "generated"),
        knowledge_adapter="aether-knowledge",
        validation_commands=(("just", "docs-check"), ("just", "verify")),
        labels={"constitutional": "Constitutional", "normative": "Normative", "canonical": "Canonical"},
    )
