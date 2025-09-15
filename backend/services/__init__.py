# Package services pour l'API heptuple

from .auth_service import AuthService  # noqa: F401
from .search_service import SearchService  # noqa: F401
try:
    from .deepseek_service import DeepSeekService  # noqa: F401
except Exception:
    # Le service DeepSeek est optionnel selon la configuration
    DeepSeekService = None  # type: ignore





