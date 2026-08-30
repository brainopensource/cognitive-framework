from ..core.models import ProviderResult
from ..core.registry import AtlasContext, Provider

class BaseProvider:
    name = "base"
    def available(self, ctx: AtlasContext) -> bool: return True
    def collect(self, ctx: AtlasContext) -> ProviderResult: return ProviderResult(self.name)
