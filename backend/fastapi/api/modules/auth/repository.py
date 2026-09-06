from core.database import DatabaseDep
from .model import Auth


class AuthRepository:
    def __init__(self, db: DatabaseDep):
        self.db = db
        self.model = Auth

    def create_user(self) -> None:
        pass
