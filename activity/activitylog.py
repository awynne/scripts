from peewee import *
from pprint import pprint
from copy import copy
import sys, os, inspect, traceback
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
        ls_model(args.list)
    elif (args.list_all):
        for table in db.get_tables():
            print table.title()
    elif (args.add):
        switcher = {
            'Activity': add_activity,
            'Location': add_location
        }
        try:
            func = switcher.get(args.add)
            func()
        except:
            print "Cannot add: %s" % args.add
            traceback.print_exc()
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

def input_model(model_str):
    clazz = globals()[model_str]
    instance = clazz.select().where(clazz.is_abstract == False).order_by(clazz.name)[0]

    while True:
        uinput = raw_input("%s name [%s]: " % (model_str, instance.name))
        if uinput == 'help':
            print "\nAvailable %ss:" % model_str
            ls_model(model_str)
            print
        else:
            try:
                if uinput == '':
                    uinput = instance.name
                clazz = globals()[model_str]
                return clazz.get(clazz.name == uinput)
            except DoesNotExist:
                print "No such AcitivityType: %s" % uinput

def input_date():
    default = datetime.today().strftime("%Y-%m-%d")
    while True:
        uinput = raw_input("date [%s]: " % default)
        if uinput == 'help':
            print "\nFormat: yyyy-mm-dd"
            print
        else:
            if uinput == '':
                uinput = default
            try:
                return datetime.strptime(uinput, "%Y-%m-%d")
            except ValueError:
                print "Invalid date: %s" % uinput

def input_time(adate, prompt):
    while True:
        uinput = raw_input(prompt)
        if uinput == 'help':
            print "\nFormat: HH:MM"
            print
        try:
            t = datetime.strptime(uinput, "%H:%M")
            return datetime.combine(adate, time(t.hour, t.minute))
        except ValueError:
            print "Invalidtime: %s" % uinput

def input_int():
    while True:
        uinput = raw_input("distance: ")
        if (uinput == ""):
            return 0
        else:
            try:
                return int(uinput)
            except:
                print "Not an integer: %s" % uinput

def input_string(prompt, help_text):
    while True:
        uinput = raw_input("%s: " % prompt)

        if uinput == "help":
            print help_text
        elif uinput != "":
            return str(uinput)

def input_yn(prompt):
    while True:
        uinput = raw_input(prompt)
        if (uinput == 'y' or uinput == 'Y'):
            return True
        elif (uinput == 'n' or uinput == 'N'):
            return False

def add_location():
    print "Creating new Location [also try 'help'] ..."

    nm = input_string("name", "name is a unique identifier")
    addr = input_string("address", "Example: 123 Main St, City, State 12345")

    print "\nCreated Location: {name: %s, address: %s}" % (nm, addr)

    save = input_yn("\nSave Location (y/n)? ")
    if save == True:
        Location.create(name=nm, address=addr)
        print "Saved"
    else:
        print "Not saved"

def add_activity():
    activity = Activity()
    print "Creating new Activity [also try 'help'] ..."

    activity.activityType = input_model("ActivityType")

    adate = input_date()
    activity.start = input_time(adate, "start time: ")
    activity.end = input_time(adate, "end time: ")

    activity.person = input_model("Person")
    activity.location = input_model("Location")
    activity.distance = input_int()

    print "\nCreated Activity:"
    ls_instance(activity)

    save = input_yn("\nSave Activity (y/n)? ")
    if save == True:
        activity.save()
        print "Saved"
    else:
        print "Not saved"

def ls_model(clazzStr):
    clazz = globals()[clazzStr]
    for item in clazz.select():
        if item.is_abstract == False:
            ls_instance(item)

def ls_instance(instance):
    attrs = copy(vars(instance)['_data'])
    del(attrs['is_abstract'])
    pprint(attrs)

if __name__ == '__main__':
    main(sys.argv[1:])

