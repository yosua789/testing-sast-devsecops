import mongoengine as me
from dataclasses import dataclass
from datetime import datetime

@dataclass
class InputPath:
    host:str
    docker:str

@dataclass
class AddLog:
    filename:str
    path:str


class PathModel(me.Document):
    meta = {"collection" : "path"}

    host_path = me.StringField(required=True)
    docker_path = me.StringField(required=True)
    created_at = me.DateTimeField(required=True, default=datetime.now)

class LogModel(me.Document):
    meta = {"collection" : "log_file"}

    filename = me.StringField(required=True)
    lastsize = me.IntField(required=True,default=0)
    dateformat = me.StringField(required=True)
    path = me.ReferenceField(PathModel,required=True)
    created_at = me.DateTimeField(required=True, default=datetime.now)

class MetaModel(me.Document):
    meta = {"collection" : "metadata"}
    
    filelog = me.ReferenceField(LogModel,required=True)
    data = me.StringField(required=True)
    created_at = me.DateTimeField(required=True, default=datetime.now)
