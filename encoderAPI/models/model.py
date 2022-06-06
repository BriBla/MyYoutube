from datetime import datetime
import sqlalchemy
from sqlalchemy import sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import re

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(45))
    email = sqlalchemy.Column(sqlalchemy.String(45))
    pseudo = sqlalchemy.Column(sqlalchemy.String(45))
    password = sqlalchemy.Column(sqlalchemy.String(45))
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP(), server_default="CURRENT_TIMESTAMP")
    token = relationship("Token", back_populates="user", cascade="all, delete", passive_deletes=True)
    videos = relationship("Video", back_populates="user", cascade="all, delete", passive_deletes=True)
    comments = relationship("Comment", back_populates="user", cascade="all, delete", passive_deletes=True)

    @property
    def serialize(user):
        return{
            "id": user.id,
            "username": user.username,
            "pseudo": user.pseudo,
            "created_at": user.formattedDate,
        }

    @property
    def serializeAuth(user):
        return{
            "id": user.id,
            "username": user.username,
            "pseudo": user.pseudo,
            "created_at": user.formattedDate,
            "email": user.email
        }
    @property
    def validateAttributes(user) -> bool:
        user_re = re.compile("^[a-zA-Z0-9_-]+$")
        email_re = re.compile("^([\w-]+|\w+\.\w+)+@[\w-]+(\.[a-z]{2,})+$")
        if not user_re.match(user.username):
            return False
        if not email_re.match(user.email):
            return False
        if not user.password:
            return False
        return True

    @property
    def validateAttributes(user) -> dict:
        user_re = re.compile("^[a-zA-Z0-9_-]+$")
        email_re = re.compile("^([\w-]+|\w+\.\w+)+@[\w-]+(\.[a-z]{2,})+$")
        return_dict = {}
        if not user_re.match(user.username):
            return_dict["username"] = "Invalid username"
        if not email_re.match(user.email):
            return_dict["email"] = "Invalid email"
        if not user.password:
            return_dict["password"] = "Invalid password"
        return return_dict

    @property
    def formattedDate(user) -> str:
        date = user.created_at
        return str(f"{date.year}-{date.month}-{date.day} {date.hour:0>2}:{date.minute:0>2}")



class Token(Base):
    __tablename__ = "token"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.String(255))
    expired_at = sqlalchemy.Column(sqlalchemy.DateTime())
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("user.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="token")

    @property
    def serialize(token):
        return {
            #"id": token.id,
            "token": token.code,
            #"expired_at": formatDate(token.expired_at),
            "user": token.user.serializeAuth,
        }



class Video(Base):
    __tablename__ = "video"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    duration = sqlalchemy.Column(sqlalchemy.Integer(), nullable=True)
    source = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP(), server_default="CURRENT_TIMESTAMP", nullable=False)
    view = sqlalchemy.Column(sqlalchemy.Integer(), nullable=False)
    enabled = sqlalchemy.Column(sqlalchemy.SmallInteger(), nullable=False)
    source_resolution = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("user.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="videos")
    formats = relationship("VideoFormat", back_populates="video", cascade="all, delete", passive_deletes=True)
    
    @property
    def serialize(video):
        return{
            "id": video.id,
            "name": video.name,
            "source": video.source.split('/')[-1],
            "user": video.user.serialize,
            "enabled": video.enabled,
            "views": video.view,
            "created_at": formatDate(video.created_at),
            "duration": video.duration
        }
    @property
    def serializeAuth(video):
        return{
            "id": video.id,
            "name": video.name,
            "source": video.source.split('/')[-1],
            "user": video.user.serializeAuth,
            "enabled": video.enabled,
            "views": video.view,
            "created_at": formatDate(video.created_at),
            "duration": video.duration
        }
    
    def redoName(self):
        ext_id = self.name.rfind('.')
        if ext_id > 0:
            new_name = self.name[0:ext_id] + str(int(datetime.now().timestamp())) + "_" + str(self.user_id) + self.name[ext_id:]
        else:
            new_name = self.name + str(int(datetime.now().timestamp())) + "_" + str(self.user_id)
        self.name = new_name


class Format(Base):
    __tablename__ = "format"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    resolution = sqlalchemy.Column(sqlalchemy.String(255))

class VideoFormat(Base):
    __tablename__ = "video_format"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    source = sqlalchemy.Column(sqlalchemy.String(255))
    resolution = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    format_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("format.id", ondelete='CASCADE'))
    video_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("video.id", ondelete='CASCADE'))
    video = relationship("Video", back_populates="formats")

class Comment(Base):
    __tablename__ = "comment"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    body = sqlalchemy.Column(sqlalchemy.Text())
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("user.id", ondelete='CASCADE'))
    video_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("video.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="comments")

    @property
    def serialize(comment):
        return{
            "id": comment.id,
            "body": comment.body,
            "user": comment.user.serialize,
        }
    @property
    def serializeAuth(comment):
        return{
            "id": comment.id,
            "body": comment.body,
            "user": comment.user.serializeAuth,
        }



def formatDate(date: datetime):
    return str(f"{date.year}-{date.month}-{date.day} {date.hour:0>2}:{date.minute:0>2}")
