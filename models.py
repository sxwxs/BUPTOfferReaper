import os
from peewee import *

DB_URL_ENV_KEY = "DB_URI"

db = SqliteDatabase(os.environ[DB_URL_ENV_KEY] if DB_URL_ENV_KEY in os.environ else "main.db")


class BaseModel(Model):
    class Meta:
        database = db


class Offer(BaseModel):
    id = AutoField()
    company = TextField()
    org = TextField()
    title = TextField()
    industry = TextField()
    location = TextField()
    salary = TextField()
    bonus = TextField()
    package = TextField()
    note = TextField()
    hukou = TextField()
    level = TextField()
    type_ = TextField()
    comments = TextField()
    key = TextField()
    difficulty = TextField()
    up_count = IntegerField(default=0)
    down_count = IntegerField(default=0)
    created = DateTimeField()



class Comment(BaseModel):
    id = AutoField()
    offer = ForeignKeyField(Offer, backref='user_comments')
    comment = TextField()
    ip = TextField()
    created = DateTimeField()


class Mark(BaseModel):
    id = AutoField()
    offer = ForeignKeyField(Offer, backref='user_marks')
    mark = IntegerField()
    ip = TextField()
    created = DateTimeField()
