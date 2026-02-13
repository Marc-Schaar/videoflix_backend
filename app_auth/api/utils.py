import uuid


def create_username(email):
    base_username = email.split("@")[0]
    base_username = base_username[:130]
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{base_username}_{unique_suffix}"
