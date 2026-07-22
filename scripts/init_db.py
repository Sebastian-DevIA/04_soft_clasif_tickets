import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.models import Base
from src.db.session import engine


def main() -> None:
    Base.metadata.create_all(engine)
    print("Tablas creadas:", list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()
