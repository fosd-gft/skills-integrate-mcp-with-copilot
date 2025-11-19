"""Server package for the Mergington High School API."""

from .database import init_db, get_activities_dict, signup, unregister

__all__ = ["init_db", "get_activities_dict", "signup", "unregister"]
