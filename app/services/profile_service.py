from .permission_service import ALLOWED_PROFILE_FIELDS
from ..extensions import db
from ..models import PublicationLink


def update_member_profile(member, payload):
    allowed = {key: payload[key] for key in ALLOWED_PROFILE_FIELDS if key in payload}

    if "bio" in allowed:
        member.bio = allowed["bio"]
    if "email" in allowed:
        member.email = allowed["email"]
    if "publication_links" in allowed:
        replace_publication_links(member, allowed["publication_links"])

    db.session.commit()
    return member


def replace_publication_links(member, links):
    if not isinstance(links, list):
        raise ValueError("publication_links must be a list")

    member.publication_links.clear()
    for index, link in enumerate(links):
        title = str(link.get("title", "")).strip() if isinstance(link, dict) else ""
        url = str(link.get("url", "")).strip() if isinstance(link, dict) else ""
        if not title or not url:
            raise ValueError("Each publication link requires title and url")
        year = normalize_year(link.get("year"))
        member.publication_links.append(
            PublicationLink(
                title=title,
                journal=(link.get("journal") or None),
                year=year,
                url=url,
                display_order=link.get("display_order", (index + 1) * 10),
            )
        )


def normalize_year(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Publication year must be a number") from exc
