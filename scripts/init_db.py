from memory.postgres.session import engine
from memory.postgres.base import Base


def main() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
