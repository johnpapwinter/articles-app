from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    '''Base class for all database models'''

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns.values()
        }


