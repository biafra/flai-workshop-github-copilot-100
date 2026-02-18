import copy
import pytest
from fastapi.testclient import TestClient

from app import app, activities

# Snapshot initial participants so tests can be isolated
_ORIGINAL_PARTICIPANTS = {
    name: list(data["participants"]) for name, data in activities.items()
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore all participant lists to their original state before each test."""
    for name, original in _ORIGINAL_PARTICIPANTS.items():
        activities[name]["participants"] = list(original)
    yield


@pytest.fixture
def client():
    return TestClient(app)
