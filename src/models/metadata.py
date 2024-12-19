import mongoengine as me
from dataclasses import dataclass
from datetime import datetime

class MetaModel(me.Document):
    meta = {"collection" : "metadata"}

    name = me.StringField(required=True)
    data = me.StringField(required=True)
    created_at = me.DateTimeField(required=True, default=datetime.now)

class LogModel(me.Document):
    meta = {"collection" : "log_file"}

    filename = me.StringField(required=True)
    lastsize = me.IntField(required=True,default=0)
    created_at = me.DateTimeField(required=True, default=datetime.now)

    