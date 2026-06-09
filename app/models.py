from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255))
    role = db.Column(db.Enum("member", "admin"), nullable=False, default="member")
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    member = db.relationship("Member", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(str(password or ""))

    def check_password(self, password):
        return bool(self.password_hash) and check_password_hash(
            self.password_hash, str(password or "")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "campus_id": self.campus_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    campus_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    role = db.Column(
        db.Enum("pi", "postdoc", "phd", "master", "undergrad", "alumni"),
        nullable=False,
    )
    title = db.Column(db.String(160))
    avatar_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    email = db.Column(db.String(255))
    active = db.Column(db.Boolean, nullable=False, default=True)
    display_order = db.Column(db.Integer, nullable=False, default=100)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    user = db.relationship("User", back_populates="member")
    publication_links = db.relationship(
        "PublicationLink",
        back_populates="member",
        cascade="all, delete-orphan",
        order_by="PublicationLink.display_order, PublicationLink.id",
    )

    def to_dict(self, include_publications=True):
        data = {
            "id": self.id,
            "campus_id": self.campus_id,
            "name": self.name,
            "slug": self.slug,
            "role": self.role,
            "title": self.title,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "email": self.email,
            "active": self.active,
            "display_order": self.display_order,
        }
        if include_publications:
            data["publication_links"] = [
                publication.to_dict() for publication in self.publication_links
            ]
        return data


class PublicationLink(db.Model):
    __tablename__ = "publication_links"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    journal = db.Column(db.String(255))
    year = db.Column(db.Integer)
    url = db.Column(db.String(500), nullable=False)
    display_order = db.Column(db.Integer, nullable=False, default=100)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    member = db.relationship("Member", back_populates="publication_links")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "journal": self.journal,
            "year": self.year,
            "url": self.url,
            "display_order": self.display_order,
        }
