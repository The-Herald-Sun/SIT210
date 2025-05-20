from peewee import AutoField, IntegerField, TextField, Model
from Db import db
from .BaseModel import BaseModel

class Cow(BaseModel):
    id = AutoField(primary_key=True)
    tag_id = TextField(unique=True)
    name = TextField()
    feed_time = IntegerField()

    def __str__(self):
        return f'Cow ID: {self.id}, Tag ID: {self.tag_id},Name: {self.name}, Feed Time: {self.feed_time:.3g}s'

def create_tables():
    with db:
        db.create_tables([Cow])

if __name__ == '__main__':
    # saves the effort of writing sql
    create_tables()