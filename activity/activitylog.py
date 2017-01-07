from peewee import *
from pprint import pprint
from copy import copy
import sys, os, inspect
import argparse
import inspect
from datetime import datetime
from datetime import time

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
    elif (args.add):
        switcher = {
            'Activity': addActivity
        }
        func = switcher.get(args.add)
        func()
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
    parser.add_argument('--add', metavar='<model-class>', dest='add', 
                        help='Add an instance of the specified class')

    return parser.parse_args()

def addActivity():
    activity = Activity()
    print "Creating new Activity [also try 'help'] ..."

    type_input = raw_input("activityType: " )
    activity.activityType = ActivityType.get(ActivityType.name == type_input)

    date_in = raw_input("date: ")
    adate = datetime.strptime(date_in, "%Y-%m-%d")

    start_in = raw_input("start time: ")
    start_t = datetime.strptime(start_in, "%H:%M")
    activity.start = datetime.combine(adate, time(start_t.hour, start_t.minute))

    end_in = raw_input("end time: ")
    end_t = datetime.strptime(end_in, "%H:%M")
    activity.end = datetime.combine(adate, time(end_t.hour, end_t.minute))

    person_in = raw_input("person name: ")
    activity.person = Person.get(Person.name == person_in)

    location_in = raw_input("location: ")
    activity.location = Location.get(Location.name == location_in)

    dist_in = raw_input("distance: ")
    if (dist_in != ""):
        activity.distance = int(dist_in)

    activity.save()
    print "\nCreated:"
    lsInstance(activity)

def addModel(clazzStr):
    clazz = globals()[clazzStr]
    instance = clazz()

    attributes = inspect.getmembers(clazz, lambda a:not(inspect.isroutine(a)))
    attributes = [a for a in attributes if not(a[0].startswith('_') 
        or a[0].endswith('_id') 
        or a[0] == 'id'
        or a[0] == 'is_abstract' 
        or a[0] == 'dirty_fields'
        or a[0] == 'DoesNotExist'
    )]

    for attr in attributes:
        field = str(attr[0])
        print "field: %s" % field
        try: 
            x = getattr(instance, field)
            print "%s [%s]: " % (field, x)
        except DoesNotExist:
            print "%s []: " % (field)
        print

           #setattr(instance, field, 88)

def lsModel(clazzStr):
    clazz = globals()[clazzStr]
    for item in clazz.select():
        if item.is_abstract == False:
            lsInstance(item)

def lsInstance(instance):
    attrs = copy(vars(instance)['_data'])
    del(attrs['is_abstract'])
    print
    pprint(attrs)

if __name__ == '__main__':
    main(sys.argv[1:])

