from datetime import date, datetime, time, timezone

from sqlmodel import Field, Session, SQLModel, create_engine, select


class SavedChart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    gender: str
    dob: date
    tob: time
    pob_label: str
    latitude: float
    longitude: float
    tz_name: str
    utc_offset: float  # computed from tz_name + dob/tob at save time; stored for display
    chart_json: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


_engine = None


def init_db(db_path: str = "jathakam.db") -> None:
    global _engine
    _engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(_engine)


def get_engine():
    if _engine is None:
        raise RuntimeError("init_db() must be called before using the database")
    return _engine


def save_chart(chart: SavedChart) -> SavedChart:
    with Session(get_engine()) as session:
        session.add(chart)
        session.commit()
        session.refresh(chart)
        return chart


def list_charts() -> list[SavedChart]:
    with Session(get_engine()) as session:
        return list(session.exec(select(SavedChart).order_by(SavedChart.created_at.desc())))


def get_chart(chart_id: int) -> SavedChart | None:
    with Session(get_engine()) as session:
        return session.get(SavedChart, chart_id)


def delete_chart(chart_id: int) -> bool:
    with Session(get_engine()) as session:
        chart = session.get(SavedChart, chart_id)
        if chart is None:
            return False
        session.delete(chart)
        session.commit()
        return True
