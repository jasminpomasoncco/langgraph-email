from .email_categorizer import categorize_email
from .email_writer import query_or_email, write_email_with_context


class _LazyAgentRegistry:
    """Registry that builds each agent chain on first access and caches it.

    Building a chain can be expensive (it may spin up the vector store), so we
    avoid doing it at import time.
    """

    _factories = {
        "email_categorizer": categorize_email,
        "query_or_email": query_or_email,
        "write_email_with_context": write_email_with_context,
    }

    def __init__(self):
        self._cache = {}

    def __getitem__(self, name):
        if name not in self._cache:
            try:
                factory = self._factories[name]
            except KeyError:
                raise KeyError(f"Unknown agent: {name!r}") from None
            self._cache[name] = factory()
        return self._cache[name]

    def __contains__(self, name):
        return name in self._factories


AGENT_REGISTRY = _LazyAgentRegistry()
