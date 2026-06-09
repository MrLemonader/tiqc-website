from .extensions import db
from .models import Member, PublicationLink, User


def seed_demo_data():
    if User.query.filter_by(campus_id="20240001").first():
        return

    alice = User(campus_id="20240001", name="Alice Chen", email="alice@example.edu")
    bob = User(campus_id="20240002", name="Bob Li", email="bob@example.edu")
    admin = User(
        campus_id="admin001",
        name="TIQC Admin",
        email="admin@example.edu",
        role="admin",
    )
    alice.set_password(alice.campus_id)
    bob.set_password(bob.campus_id)
    admin.set_password(admin.campus_id)
    db.session.add_all([alice, bob, admin])
    db.session.flush()

    alice_member = Member(
        user_id=alice.id,
        campus_id=alice.campus_id,
        name=alice.name,
        slug="alice-chen",
        role="phd",
        title="PhD Student",
        email=alice.email,
        bio="Researching trapped-ion quantum computing and control systems.",
        display_order=10,
    )
    bob_member = Member(
        user_id=bob.id,
        campus_id=bob.campus_id,
        name=bob.name,
        slug="bob-li",
        role="postdoc",
        title="Postdoctoral Researcher",
        email=bob.email,
        bio="Working on quantum information processing and experimental platforms.",
        display_order=20,
    )
    db.session.add_all([alice_member, bob_member])
    db.session.flush()

    db.session.add(
        PublicationLink(
            member_id=alice_member.id,
            title="Example publication link",
            journal="Internal Demo Journal",
            year=2026,
            url="https://example.edu/publication",
            display_order=10,
        )
    )
    db.session.commit()
