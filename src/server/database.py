import os
from sqlalchemy import (create_engine, Column, Integer, String, Text, ForeignKey)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    schedule = Column(String)
    max_participants = Column(Integer, default=0)
    participants = relationship("Participant", back_populates="activity", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", back_populates="participants")


SessionLocal = None


def init_db(db_url: str | None = None):
    """Initialize the SQLite database and create tables.

    If `db_url` is not provided, a local file `data/app.db` is used.
    """
    global SessionLocal
    if not db_url:
        os.makedirs("data", exist_ok=True)
        db_url = "sqlite:///data/app.db"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed a few activities if the DB is empty so the app behaves like before
    session = SessionLocal()
    try:
        count = session.query(Activity).count()
        if count == 0:
            seed = [
                {
                    "name": "Chess Club",
                    "description": "Learn strategies and compete in chess tournaments",
                    "schedule": "Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 12,
                    "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
                },
                {
                    "name": "Programming Class",
                    "description": "Learn programming fundamentals and build software projects",
                    "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                    "max_participants": 20,
                    "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
                },
                {
                    "name": "Gym Class",
                    "description": "Physical education and sports activities",
                    "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                    "max_participants": 30,
                    "participants": ["john@mergington.edu", "olivia@mergington.edu"],
                },
            ]

            for a in seed:
                activity = Activity(
                    name=a["name"],
                    description=a["description"],
                    schedule=a["schedule"],
                    max_participants=a["max_participants"],
                )
                session.add(activity)
                session.flush()
                for email in a["participants"]:
                    session.add(Participant(email=email, activity_id=activity.id))

            session.commit()
    finally:
        session.close()


def _get_session():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return SessionLocal()


def get_activities_dict():
    """Return activities in the same dict format the app used previously."""
    session = _get_session()
    try:
        activities = {}
        for a in session.query(Activity).all():
            activities[a.name] = {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": [p.email for p in a.participants],
            }
        return activities
    finally:
        session.close()


def signup(activity_name: str, email: str):
    session = _get_session()
    try:
        activity = session.query(Activity).filter_by(name=activity_name).first()
        if activity is None:
            raise KeyError("Activity not found")

        # Check existing
        for p in activity.participants:
            if p.email == email:
                raise ValueError("Student is already signed up")

        participant = Participant(email=email, activity_id=activity.id)
        session.add(participant)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        session.close()


def unregister(activity_name: str, email: str):
    session = _get_session()
    try:
        activity = session.query(Activity).filter_by(name=activity_name).first()
        if activity is None:
            raise KeyError("Activity not found")

        participant = None
        for p in activity.participants:
            if p.email == email:
                participant = p
                break

        if participant is None:
            raise ValueError("Student is not signed up for this activity")

        session.delete(participant)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        session.close()
