import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from datetime import datetime, timezone

from app import login, db


@login.user_loader
def load_user(user_id: str) -> Optional['User']:
    return db.session.get(User, int(user_id))


followers = db.Table('followers',
                     db.metadata,
                     sa.Column('follower_id', sa.Integer, db.ForeignKey('user.id'), primary_key=True),
                     sa.Column('followed_id', sa.Integer, db.ForeignKey('user.id'), primary_key=True)
                     )


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True)
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(240))
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(240))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    posts: so.Mapped['Post'] = so.relationship(back_populates='author')

    following: so.Mapped['User'] = so.relationship(secondary=followers,
                                                   primaryjoin=followers.c.follower_id == id,
                                                   secondaryjoin=followers.c.followed_id == id,
                                                   back_populates='followers')

    followers: so.Mapped['User'] = so.relationship(secondary=followers,
                                                   primaryjoin=followers.c.followed_id == id,
                                                   secondaryjoin=followers.c.follower_id == id,
                                                   back_populates='following')

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def avatar(self, size: int) -> str:
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def following_posts(self):
        Author: User = so.aliased(User)
        Follower: User = so.aliased(User)
        agaga = (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Author.id == self.id,
                Follower.id == self.id
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )
        compiled = agaga.compile()
        print(compiled.string)
        return agaga

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(120))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates="posts")


class Role(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))
    role: so.Mapped[str] = so.mapped_column(sa.String(64))
