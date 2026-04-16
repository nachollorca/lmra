"""Logic to expose functions to the model."""

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Protocol, cast


class HasMetadata(Protocol):
    """Protocol for objects that have __name__ and __doc__."""

    __name__: str
    __doc__: str | None


@dataclass(frozen=True)
class Tool:
    """Metadata wrapper around a user-provided function.

    Attributes:
        fn: The original callable.
        name: Function name (used as the namespace key).
        short_description: First line of the docstring.
        full_description: Full signature and docstring for discovery.
    """

    fn: Callable[..., Any]
    name: str
    short_description: str
    full_description: str

    @classmethod
    def from_function(cls, fn: Any) -> "Tool":
        """Build a ``Tool`` from a plain function."""
        # We use Any for fn to avoid complex Protocol issues with Callables,
        # but we know it should have __name__ if it's a function.
        name = getattr(fn, "__name__", "unknown")
        doc = inspect.cleandoc(getattr(fn, "__doc__", "") or "")
        short = doc.split("\n", 1)[0] if doc else ""
        sig = inspect.signature(fn)
        full = f"{name}{sig}\n\n{doc}" if doc else f"{name}{sig}"
        return cls(fn=fn, name=name, short_description=short, full_description=full)


def tool(fn: Any) -> Tool:
    """Decorator that turns a function into a ``Tool``."""
    return Tool.from_function(fn)


def make_disclose_fn(tools: list[Tool]) -> Callable:
    """Build the ``disclose`` closure injected into the agent namespace.

    This is a *closure factory*: it builds ``lookup`` once from *tools*,
    then returns an inner function that captures ``lookup``.  Each call to
    ``make_disclose_fn`` produces a fresh ``disclose`` bound to exactly the
    tools registered for that ``run()`` invocation.

    Args:
        tools: The list of tools registered for this run.

    Returns:
        A callable ``(name: str) -> str``.
    """
    lookup = {t.name: t.full_description for t in tools}

    def disclose(name: str) -> str:
        """Reveal the full signature and docstring of a tool.

        Args:
            name: The tool name to look up.

        Returns:
            The full description string, or an error message if not found.
        """
        if name in lookup:
            return lookup[name]
        available = ", ".join(lookup) or "(none)"
        return f"Unknown tool: {name!r}. Available tools: {available}"

    return disclose
