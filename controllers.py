"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from . common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from . models import get_user_email
from py4web.utils.form import Form, FormStyleBulma

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth.user, 'index.html')
def index():
    
    logged_in_user = auth.current_user.get('email')
    rows = db(db.cs_class).select().as_list()

        # We read all the contact rows as a list (see below). 

    # and then we iterate on each one, to add the phone numbers for the contact. 
    
    for row in rows:
        # Here we must fish out of the db the phone numbers 
        # attached to the contact, and produce a nice string like 
        # "354242 (Home), 34343423 (Vacation)" for the contact. 
        studentList =  db(db.student.class_id == row['id']).select().as_list()
        
        s = ""
        for student in studentList:
            s += student['student_name'] + " (" + student['year'] + ') '
        # # and we can simply assign the nice string to a field of the row!  
        # # No matter that the field did not originally exist in the database.
        row["students"] = s
    # So at the end, we can return "nice" rows, each one with our nice string. 
    # A row r will have fields r["first_name"], r["last_name"], r["phone_numbers"], ... 
    # You can pass these rows to the view, so you can display the table. 
    classes = db(db.student.student_email == auth.current_user.get('email')).select().as_list()
    print(classes)
    classesTaken = []
    for course in classes:
        className = db.cs_class[course["class_id"]]
        classesTaken.append(className["className"])
    print(classesTaken)
    percent = (len(classesTaken) / 4) * 100
    return dict(rows = rows, url_signer = url_signer, classesTaken = classesTaken, percent=percent)

# @action('add', method = ["GET", "POST"])
# @action.uses(db, auth.user, 'add.html')
# def add():
    
#     form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('index'))
#     return(dict(form=form))

# @action('edit/<contact_id:int>',method=["GET","POST"])
# @action.uses(db, session, auth.user, 'edit.html')
# def edit(contact_id = None):
#     assert contact_id is not None
#     p = db.contact[contact_id]
#     if p is None:
#         redirect(URL('index'))
#     form = Form(db.contact, record = p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('index'))
#     return dict(form=form)


# @action('delete/<contact_id:int>', method=["GET"])
# @action.uses(db, session, auth.user, url_signer.verify())
# def delete(contact_id = None):
#     assert contact_id is not None
#     db(db.contact.id == contact_id).delete()
#     redirect(URL('index'))

# @action('edit_phones/<contact_id:int>', method=["GET","POST"])
# @action.uses(db, session, auth.user, 'edit_phones.html')
# def edit_phones(contact_id = None):
#     assert contact_id is not None
#     p = db.contact[contact_id]
#     if p is None:
#         redirect(URL('index'))
#     rows = db(db.phone.contact_id == contact_id).select()
#     return dict(rows=rows, name=p['className'], contact=contact_id)

@action('add_student/<class_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_student.html')
def add_student(class_id = None):
    assert class_id is not None
    p = db.cs_class[class_id]
    if p is None:
        redirect(URL('index'))
    form = Form(db.student, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form, className=p['className'])
    
 


@action('remove_student/<class_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user)
def remove_student(class_id=None):
    assert class_id is not None
    db((db.student.student_email == auth.current_user.get("email")) & (db.student.class_id == class_id)).delete()
    redirect(URL('index'))



# @action('add_phone/<contact_id:int>', method=["GET","POST"])
# @action.uses(db, session, auth.user, 'add_phone.html')
# def add_phone(contact_id = None):
#     assert contact_id is not None
#     p = db.contact[contact_id]
#     if p is None:
#         redirect(URL('index'))
#     form = Form(db.phone, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL("edit_phones", contact_id))
#     return dict(form=form, name=p['firstName'])

# @action('edit_phone/<contact_id:int>/<phone_id:int>', method=["GET", "POST"])
# @action.uses(db, session, auth.user, 'edit_phone.html')
# def edit_phone(contact_id=None, phone_id=None):
#     assert contact_id is not None
#     assert phone_id is not None
#     p = db.phone[phone_id]
#     if p is None:
#         redirect(URL('edit_phones', contact_id))
#     form = Form(db.phone, record = p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('edit_phones', contact_id))
#     return dict(form=form, name=db.contact[contact_id]["firstName"])

# @action('delete_phone/<contact_id:int>/<phone_id:int>', method=["GET"])
# @action.uses(db, session, auth.user)
# def delete_phone(contact_id=None, phone_id=None):
#     assert contact_id is not None
#     assert phone_id is not None
#     db(db.phone.id == phone_id).delete()
#     redirect(URL('edit_phones',contact_id))

    