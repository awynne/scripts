from peewee import *
from pprint import pprint
from copy import copy
import sys, getopt, os, inspect

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
    try:
        opts, args = getopt.getopt(argv, "", ["ls=", "la"])
        if not opts:
            usage()
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt == '--ls':
            lsModel(arg)
        elif opt == '--la':
            for table in db.get_tables():
                print table.title()
        else:
            usage()

def usage():
    script = os.path.basename(__file__)
    print "%s --ls <modelClass>" % script
    sys.exit(2)

def lsModel(clazzStr):
    clazz = globals()[clazzStr]

    for item in clazz.select():
        if item.is_abstract == False:
            attrs = copy(vars(item)['_data'])
            del(attrs['is_abstract'])
            pprint(attrs)

if __name__ == '__main__':
    main(sys.argv[1:])

