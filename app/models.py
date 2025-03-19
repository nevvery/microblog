import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional

from app import login, db


@login.user_loader
def load_user(user_id: str) -> Optional['User']:
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True)

    password_hash: so.Mapped[str] = so.mapped_column(sa.String(240))

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)
