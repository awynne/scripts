from peewee import *
from pprint import pprint
from copy import copy
import sys, os, inspect
import optparse
import argparse

db = SqliteDatabase('activitylog.db')

################
# Model classes
################

class BaseModel(Model):
    is_abstract = BooleanField(default=False)

    class Meta:
        database = db

class NamedModel(BaseModel):
    name = CharField(primary_key=True)

class Person(NamedModel):
    first = CharField()
    last = CharField()
    born = DateField()

class ActivityType(NamedModel):
    parent = ForeignKeyField('self', null=True, related_name='children')

class MeasurementType(NamedModel):
    parent = ForeignKeyField('self', null=True, related_name='children')

class Location(NamedModel):
    address = CharField()

class Entry(BaseModel):
    person = ForeignKeyField(Person)
    location = ForeignKeyField(Location)
    props = CharField(null=True)

class Activity(Entry):
    start = DateTimeField()
    end = DateTimeField()
    activityType = ForeignKeyField(ActivityType)
    distance = IntegerField(default=0)

class Measurement(Entry):
    time = DateTimeField()
    measurementType = ForeignKeyField(MeasurementType)
    value = DecimalField()

############
# Functions
############

def main(argv):
    args = parse_args();

    if args.list:
        lsModel(args.list)
    elif (args.list_all):
        for table in db.get_tables():
            print table.title()
    else:
        script = os.path.basename(__file__)
        print "%s: you must specify an option" % script
        exit(2)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", metavar='<model-class>', dest='list',
                        help='List model objects for the specified class')
    parser.add_argument('--list-all', dest='list_all', action='store_true', 
                        help='List all model classes')

    return parser.parse_args()

def lsModel(clazzStr):
    clazz = globals()[clazzStr]

    for item in clazz.select():
        if item.is_abstract == False:
            attrs = copy(vars(item)['_data'])
            del(attrs['is_abstract'])
            pprint(attrs)

if __name__ == '__main__':
    main(sys.argv[1:])

