from activitylog import *
from datetime import datetime
from datetime import date

def createDB():
    db.create_tables([Person, ActivityType, Activity, MeasurementType, Measurement, Location])

def defaultActivities():
    root = ActivityType.create(name="BaseActivityType", is_abstract=True)
    mindful = ActivityType.create(name="Mindful", parent=root, is_abstract=True)
    aerobic = ActivityType.create(name="Aerobic", parent=root, is_abstract=True)

    yoga = ActivityType.create(name="Yoga", parent=mindful, is_abstract=True)
    unheated_yoga = ActivityType.create(name="UnheatedYoga", parent=yoga)
    heated_yoga = ActivityType.create(name="HeatedYoga", parent=yoga)
    meditation = ActivityType.create(name="Meditation", parent=mindful)

    running = ActivityType.create(name="Running", parent=aerobic)
    hiking = ActivityType.create(name="Hiking", parent=aerobic)
    walking = ActivityType.create(name="Walking", parent=aerobic)

def defaultPeople():
    birth = date(1974,6,2)
    adam = Person.create(name="adam", first="Adam", last="Wynne", born=birth)

def defaultLocations():
    Location.create(name="YogaFlowSouth", longname="Yoga Flow South Hills", address="250 Mount Lebanon Boulevard, Pittsburgh, PA 15234")
    Location.create(name="HIP", longname="Himalayan Institute, Pittsburgh", address="300 Beverly Rd, Pittsburgh, PA 15216")
    Location.create(name="Gilfilan", longname="Gilfilan Farms", address="130 Orr Rd, Upper St Clair, PA 15241")

def testEntries():
    adam=Person.select().where(Person.name =="adam")
    hiking=ActivityType.select().where(ActivityType.name == "Hiking")
    gilfilan=Location.select().where(Location.name == "Gilfilan")

    Activity.create(start=datetime(2016,1,2,10,00,00), end=datetime.now(), person=adam, activityType=hiking, location=gilfilan, distance=3)

def init():
    createDB()
    defaultActivities()
    defaultPeople()
    defaultLocations()
    testEntries()

init()
