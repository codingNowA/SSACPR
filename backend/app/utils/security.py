from __future__ import annotations

import hashlib


def mask_email(email: str) -> str:
	if "@" not in email:
		return email
	name, domain = email.split("@", 1)
	if len(name) <= 2:
		masked_name = "*" * len(name)
	else:
		masked_name = f"{name[0]}***{name[-1]}"
	return f"{masked_name}@{domain}"


def mask_phone(phone: str) -> str:
	if len(phone) < 7:
		return phone
	return f"{phone[:3]}****{phone[-4:]}"


def hash_text(value: str) -> str:
	return hashlib.sha256(value.encode("utf-8")).hexdigest()


def secure_token(value: str) -> str:
	return hash_text(value)
