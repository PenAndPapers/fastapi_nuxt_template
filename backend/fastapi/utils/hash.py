import hashlib


def hash_token(token: str, encoding: str = "utf-8") -> str:
  return hashlib.sha256(token.encode(encoding)).hexdigest()
