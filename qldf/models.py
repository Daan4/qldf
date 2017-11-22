from qldf import db
from flask import flash
from sqlalchemy import ForeignKey
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import UnmappedInstanceError


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classmethod
    def create(cls, success_msg=None, failure_msg=None, **kwargs):
        new_record = cls(**kwargs)
        try:
            db.session.add(new_record)
            db.session.commit()
            if success_msg:
                flash(success_msg)
        except (IntegrityError, InvalidRequestError):
            db.session.rollback()
            if failure_msg:
                flash(failure_msg)

    @classmethod
    def delete(cls, success_msg=None, unmapped_msg=None, failure_msg=None, **kwargs):
        existing_record = cls.query.filter_by(**kwargs).first()
        try:
            db.session.delete(existing_record)
            db.session.commit()
            if success_msg:
                flash(success_msg)
        except UnmappedInstanceError:
            db.session.rollback()
            if unmapped_msg:
                flash(unmapped_msg)
        except IntegrityError:
            db.session.rollback()
            if failure_msg:
                flash(failure_msg)


class Player(BaseModel):
    __tablename__ = 'player'
    name = db.Column(db.Text)

    def __repr__(self):
        return f'<Player {self.id}: {self.name}>'


class Record(BaseModel):
    __tablename__ = 'record'
    mode = db.Column(db.Integer)
    map_id = db.Column(db.Integer, ForeignKey('map.id'))
    player_id = db.Column(db.Integer, ForeignKey('player.id'))
    time = db.Column(db.Integer)
    match_guid = db.Column(db.Text)

    def __repr__(self):
        return f'<Record {self.id}: {self.map_id} {self.player_id} {self.mode}>'


class Map(BaseModel):
    __tablename__ = 'map'
    name = db.Column(db.Text)
    author = db.Column(db.Text)
    workshop_url = db.Column(db.Text)

    def __repr__(self):
        return f'<Map {self.id}: {self.name}>'
