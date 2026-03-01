'''
find_matches

get_all_by_primary_ids

create_primary

create_secondary

update_to_secondary

update_linked_contacts
'''

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.contact import Contact


def find_matches(
    db: Session,
    email: Optional[str],
    phone: Optional[str]
) -> List[Contact]:

    query = db.query(Contact).filter(Contact.deletedAt.is_(None))

    filters = []
    if email:
        filters.append(Contact.email == email)
    if phone:
        filters.append(Contact.phoneNumber == phone)

    if not filters:
        return []

    return query.filter(or_(*filters)).all()


def get_all_by_primary_ids(
    db: Session,
    primary_ids: List[int]
) -> List[Contact]:

    if not primary_ids:
        return []

    return db.query(Contact).filter(
        Contact.deletedAt.is_(None),
        or_(
            Contact.id.in_(primary_ids),
            Contact.linkedId.in_(primary_ids)
        )
    ).all()


def create_primary(
    db: Session,
    email: Optional[str],
    phone: Optional[str]
) -> Contact:

    contact = Contact(
        email=email,
        phoneNumber=phone,
        linkedId=None,
        linkPrecedence="primary"
    )

    db.add(contact)
    db.flush()  # to get ID before commit

    return contact


def create_secondary(
    db: Session,
    email: Optional[str],
    phone: Optional[str],
    primary_id: int
) -> Contact:

    contact = Contact(
        email=email,
        phoneNumber=phone,
        linkedId=primary_id,
        linkPrecedence="secondary"
    )

    db.add(contact)
    db.flush()

    return contact


def update_to_secondary(
    db: Session,
    contact: Contact,
    new_primary_id: int
):
    contact.linkPrecedence = "secondary"
    contact.linkedId = new_primary_id



def update_linked_contacts(
    db: Session,
    old_primary_id: int,
    new_primary_id: int
):
    db.query(Contact).filter(
        Contact.linkedId == old_primary_id
    ).update(
        {"linkedId": new_primary_id},
        synchronize_session=False
    )