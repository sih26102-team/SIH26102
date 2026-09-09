from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ["bcrypt"],deprecated = "auto")

def get_hash_password(password:str):
    return pwd_context.hash(password)
def verify_password(plain_password:str,hashed_password:str):
    return pwd_context.verify(plain_password,hashed_password)

ALLOWED_GOVL_DOMAINS = (
    "gov.in",
    "nic.in"
)
def is_valid_gov_email(email:str):
    email_clean = email.strip().lower()
    if "@" not in email_clean:
        return False
    domain = email_clean.split("@" ,1)[1]
    return any(domain == d or domain.endswith("."+d) for d in ALLOWED_GOVL_DOMAINS)

