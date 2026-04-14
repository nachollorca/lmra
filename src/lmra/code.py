import contextlib
import io
import traceback

from sqlalchemy.orm import Session


def validate(code: str, allowed_imports: list[str] | None) -> tuple[bool, str]:
    """Use AST parsing against a set of rules to decide if the code is safe.

    Returns:
        (True, "") – code passes all rules.
        (False, "<violated rule>") – code violates a rule.
    """
    raise NotImplementedError


def execute(code: str, db_session: Session, namespace: dict) -> str:
    """Execute *code* inside a sandboxed namespace that includes *session*.

    Args:
        code: Python/SQLAlchemy code produced by the model.
        session: The session the code is allowed to operate on.
        namespace: dict of python symbols that exist for the execution.

    Returns:
        A string representation of stdout / return value / traceback.
        The namespace is modified in-place.
    """
    namespace["session"] = db_session
    buf = io.StringIO()
    try:
        compiled = compile(code, "<agent>", "exec")
        with contextlib.redirect_stdout(buf):
            exec(compiled, namespace)
    except Exception:
        return traceback.format_exc()
    return buf.getvalue() or repr(namespace.get("_result"))
