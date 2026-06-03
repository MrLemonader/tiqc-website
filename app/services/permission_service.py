ALLOWED_PROFILE_FIELDS = {"bio", "email", "publication_links"}


def sanitize_profile_payload(payload):
    return {key: value for key, value in payload.items() if key in ALLOWED_PROFILE_FIELDS}
