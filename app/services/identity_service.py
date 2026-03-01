from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.contact import Contact
from app.repositories import contact_repository as repo


def normalize_email(email: Optional[str]) -> Optional[str]:
    if email:
        return email.strip().lower()
    return None


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if phone:
        return phone.strip()
    return None


def resolve_identity(
    db: Session,
    email: Optional[str],
    phone: Optional[str]
) -> Dict[str, Any]:

    email = normalize_email(email)
    phone = normalize_phone(phone)

    with db.begin():

        # 1️⃣ Find direct matches
        matches = repo.find_matches(db, email, phone)

        # CASE A — No matches → create primary
        if not matches:
            primary = repo.create_primary(db, email, phone)

            return build_response([primary], primary.id)

        # 2️⃣ Collect all primary IDs involved
        primary_ids = set()

        for contact in matches:
            if contact.linkPrecedence == "primary":
                primary_ids.add(contact.id)
            else:
                primary_ids.add(contact.linkedId)

        # 3️⃣ Expand to full group
        full_group = repo.get_all_by_primary_ids(db, list(primary_ids))

        # 4️⃣ Determine canonical primary (oldest)
        primaries = [
            c for c in full_group if c.linkPrecedence == "primary"
        ]

        canonical_primary = min(
            primaries,
            key=lambda c: c.createdAt
        )

        canonical_id = canonical_primary.id

        # 5️⃣ Merge if multiple primaries exist
        for primary in primaries:
            if primary.id != canonical_id:
                repo.update_to_secondary(db, primary, canonical_id)
                repo.update_linked_contacts(
                    db,
                    old_primary_id=primary.id,
                    new_primary_id=canonical_id
                )

        # 6️⃣ Check if exact combination already exists
        exact_match = any(
            (
                (email is None or c.email == email) and
                (phone is None or c.phoneNumber == phone)
            )
            for c in full_group
        )

        if not exact_match:
            repo.create_secondary(db, email, phone, canonical_id)

        # 7️⃣ Fetch updated full group again
        updated_group = repo.get_all_by_primary_ids(db, [canonical_id])

        return build_response(updated_group, canonical_id)


from typing import List, Dict, Any
from app.models.contact import Contact


def build_response(
    contacts: List[Contact],
    primary_id: int
) -> Dict[str, Any]:

    # Ensure deterministic ordering (oldest first)
    contacts = sorted(contacts, key=lambda c: c.createdAt)

    primary = next(c for c in contacts if c.id == primary_id)

    emails: List[str] = []
    phones: List[str] = []
    secondary_ids: List[int] = []

    # --- Primary first ---
    if primary.email:
        emails.append(primary.email)

    if primary.phoneNumber:
        phones.append(primary.phoneNumber)

    # --- Process secondaries ---
    for contact in contacts:
        if contact.id == primary_id:
            continue

        secondary_ids.append(contact.id)

        if contact.email and contact.email not in emails:
            emails.append(contact.email)

        if contact.phoneNumber and contact.phoneNumber not in phones:
            phones.append(contact.phoneNumber)

    # Deterministic ordering of secondary IDs
    secondary_ids = sorted(secondary_ids)

    return {
        "contact": {
            "primaryContactId": primary_id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    }