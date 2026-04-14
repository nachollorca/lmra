"""Contains the logic for the sandoboxed python env on which to run the agent requested code."""

import contextlib
import io
import traceback


def validate(source: str, allowed_imports: list[str] | None) -> tuple[bool, str]:
    """Use AST parsing against a set of rules to decide if the code is safe.

    Args:
        source: Python source code produced by the model.
        allowed_imports: Whitelist of importable module names, or ``None`` to skip the check.

    Returns:
        (True, "") – code passes all rules.
        (False, "<violated rule>") – code violates a rule.
    """
    raise NotImplementedError


def execute(source: str, namespace: dict) -> str:
    """Execute *source* inside *namespace*.

    Args:
        source: Python/SQLAlchemy source code produced by the model.
        namespace: Dict of python symbols available during execution.
            **Mutated in-place** — new bindings created by the code (including
            ``_result``) persist in *namespace* after this call returns.

    Returns:
        A string representation of stdout / return value / traceback.
    """
    buf = io.StringIO()
    try:
        compiled = compile(source, "<agent>", "exec")
        with contextlib.redirect_stdout(buf):
            exec(compiled, namespace)
    except Exception:
        return traceback.format_exc()
    return buf.getvalue() or repr(namespace.get("_result"))
