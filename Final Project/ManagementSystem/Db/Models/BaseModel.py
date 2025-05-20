from peewee import Model
from Db import db

class BaseModel(Model):
    class Meta:
        database = db