import bcrypt

def get_hash_password(password: str) -> str:
    """Generate secure bcrypt hash from plaintext password."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False

ALLOWED_GOV_DOMAINS = (
    "gov.in",
    "nic.in",
    "civicshield.gov.in",
    "mplads.gov.in",
    "sih.gov.in",
    "example.com"
)

def is_valid_gov_email(email: str) -> bool:
    email_clean = email.strip().lower()
    if "@" not in email_clean:
        return False
    domain = email_clean.split("@", 1)[1]
    return any(domain == d or domain.endswith("." + d) for d in ALLOWED_GOV_DOMAINS)
