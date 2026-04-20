"""Re-export of the shared test fixtures schema so demo scripts keep working.

The source of truth is ``tests/fixtures/schema.py``. Demo scripts typically
run from the ``demo/`` directory (``python test.py``), so we make sure the
project root is on ``sys.path`` before importing.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.fixtures.schema import Author, Base, Book, get_author_catalog  # noqa: E402

__all__ = ["Author", "Base", "Book", "get_author_catalog"]
