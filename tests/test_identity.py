import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.identity_service import resolve_identity
from app.models.contact import Contact


TEST_DB_URL = "sqlite:///./test_contacts.db"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_new_identity(db):
    response = resolve_identity(db, "a@test.com", "111")

    assert response["contact"]["primaryContactId"] == 1
    assert response["contact"]["emails"] == ["a@test.com"]
    assert response["contact"]["phoneNumbers"] == ["111"]
    assert response["contact"]["secondaryContactIds"] == []


def test_secondary_creation(db):
    resolve_identity(db, "a@test.com", "111")
    response = resolve_identity(db, "b@test.com", "111")

    assert len(response["contact"]["emails"]) == 2
    assert response["contact"]["secondaryContactIds"] == [2]


def test_merge_two_primaries(db):
    resolve_identity(db, "x@test.com", "999")
    resolve_identity(db, "y@test.com", "888")

    response = resolve_identity(db, "x@test.com", "888")

    contacts = db.query(Contact).all()

    primaries = [c for c in contacts if c.linkPrecedence == "primary"]
    assert len(primaries) == 1

    assert response["contact"]["primaryContactId"] == primaries[0].id
    assert len(response["contact"]["secondaryContactIds"]) >= 1


def test_no_secondary_chain(db):
    resolve_identity(db, "x@test.com", "999")
    resolve_identity(db, "y@test.com", "888")
    resolve_identity(db, "x@test.com", "888")

    contacts = db.query(Contact).all()

    secondary_ids = [
        c.id for c in contacts if c.linkPrecedence == "secondary"
    ]

    invalid_links = [
        c for c in contacts
        if c.linkedId in secondary_ids
    ]

    assert len(invalid_links) == 0