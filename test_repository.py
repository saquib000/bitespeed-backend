from app.database import SessionLocal
from app.repositories.contact_repository import (
    create_primary,
    create_secondary,
    find_matches,
    get_all_by_primary_ids
)


def run_test():
    db = SessionLocal()

    try:
        # 1️⃣ Create Primary
        primary = create_primary(
            db,
            email="test@mail.com",
            phone="123456"
        )

        db.commit()

        print("Primary Created:")
        print("ID:", primary.id)
        print("Email:", primary.email)
        print("Phone:", primary.phoneNumber)

        # 2️⃣ Create Secondary
        secondary = create_secondary(
            db,
            email="second@mail.com",
            phone="123456",
            primary_id=primary.id
        )

        db.commit()

        print("\nSecondary Created:")
        print("ID:", secondary.id)
        print("Linked to:", secondary.linkedId)

        # 3️⃣ Test find_matches
        matches = find_matches(db, email=None, phone="123456")

        print("\nMatches for phone 123456:")
        for m in matches:
            print("Contact ID:", m.id)

        # 4️⃣ Expand full group
        primary_ids = [primary.id]
        group = get_all_by_primary_ids(db, primary_ids)

        print("\nFull Identity Group:")
        for g in group:
            print(
                "ID:", g.id,
                "| LinkedId:", g.linkedId,
                "| Precedence:", g.linkPrecedence
            )

    finally:
        db.close()


if __name__ == "__main__":
    run_test()