from peewee import *

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
    description = CharField(null=True)

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

def lsActivityType():
    for atype in ActivityType.select() :
        if atype.is_abstract == False:
            print atype.name

def lsLocation():
    for loc in Location.select():
        print "%s - %s" % (loc.name, loc.address)

def lsPerson():
    for person in Person.select():
        print "%s %s (%s), born: %s" % (person.first, person.last, person.name, person.born)

