"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
db.define_table(
    'cs_class',
    Field('className', requires=IS_NOT_EMPTY()),
    Field('classID', requires=IS_NOT_EMPTY()),

)

db.cs_class.id.readable = db.cs_class.id.writeable = False


db.define_table(
    'student',
    Field('class_id', 'reference cs_class'),
    Field('student_name', requires=IS_NOT_EMPTY()),
    Field('year', requires=IS_NOT_EMPTY()),
    Field('student_email', requires=IS_NOT_EMPTY(), default=get_user_email())
)


db.student.class_id.readable = db.student.class_id.writeable = False
db.student.id.readable = db.student.id.writeable = False




db.commit()
