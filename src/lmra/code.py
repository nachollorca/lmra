from sqlalchemy.orm import Session


# if we had a dataclass for State with just two fields, we wouldnt we have one for the validation result here
def validate(code: str, allowed_imports: list[str]) -> tuple[bool, str]:
    """Use AST parsing against a set of rules to decide if the code is safe.

    Returns:
        (True, "")               – code passes all rules.
        (False, "<violated rule>") – code violates a rule.
    """
    raise NotImplementedError


def execute(code: str, session: Session) -> str:
    """Execute *code* inside a sandboxed namespace that includes *session*.

    Args:
        code:    Python/SQLAlchemy code produced by the model.
        session: The session the code is allowed to operate on.

    Returns:
        A string representation of stdout / return value / traceback.
    """
    raise NotImplementedError
