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
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, Field
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    rows = db(
        (db.contact.user_email == get_user_email())
    ).select().as_list()

    for row in rows:
        s = " "
        numbers = db(db.phone.contact_id == row["id"]).select()
        entries = db(db.phone.contact_id == row["id"]).count()
        count = 1
        for temp in numbers:
            if count == entries:
                s += temp.phone_number
                s += " ("
                s += temp.phone_name
                s += ")"
            else:
                s += temp.phone_number
                s += " ("
                s += temp.phone_name
                s += "), "
            count += 1
        row["phone_numbers"] = s
    return dict(rows=rows, url_signer=url_signer)

@action('add_contact', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_contact.html')
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'edit_contact.html')
def edit_contact(id=None):
    assert id is not None
    p = db.contact[id]
    if p is None:
        redirect(URL('index'))
    if get_user_email() != p.user_email:
        redirect(URL('index'))
    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('delete_contact/<id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify())
def delete_contact(id=None):
    assert id is not None
    db(db.contact.id == id).delete()
    redirect(URL('index'))

@action('edit_phone/<id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'edit_phone.html')
def edit_phone(id=None):
    assert id is not None
    rows = db(db.phone.contact_id == id).select()
    rows2 = db(db.contact.id == id).select().first()
    return dict(rows=rows, rows2=rows2, url_signer=url_signer)

@action('add_phone/<id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_phone.html')
def edit_phone_entry(id=None):
    assert id is not None
    form = Form([Field('phone', requires=IS_NOT_EMPTY()), Field('kind', requires=IS_NOT_EMPTY())],
                csrf_session=session, formstyle=FormStyleBulma)
    user = db(db.contact.id == id).select().first()
    if form.accepted:
        db.phone.insert(contact_id=user.id, phone_number=form.vars['phone'], phone_name=form.vars['kind'])
        redirect(URL('index'))
    return dict(form=form)

@action('edit_phone/<id:int>/<id2:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'edit_phone_entry.html')
def edit_phone_entry(id=None, id2=None):
    assert id is not None
    assert id2 is not None
    phone = db((db.phone.id == id2) & (db.phone.contact_id == id)).select().first()
    form = Form([Field('phone', requires=IS_NOT_EMPTY()), Field('kind', requires=IS_NOT_EMPTY())],
                record=dict(phone=phone.phone_number, kind=phone.phone_name),
                deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        phone.update_record(phone_number=form.vars['phone'], phone_name=form.vars['kind'])
        redirect(URL('index'))
    return dict(form=form)

@action('delete_phone/<id:int>/<id2:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify())
def delete_contact(id=None, id2=None):
    assert id is not None
    assert id2 is not None
    db((db.phone.id == id2) & (db.phone.contact_id == id)).delete()
    redirect(URL('index'))