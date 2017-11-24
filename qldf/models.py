from qldf import db
from flask import flash
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy import func


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, index=True)
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
    steam_id = db.Column(db.Text)
    records = db.relationship('Record', backref='player', lazy=True)

    def __repr__(self):
        return f'<Player {self.id}>'


class Record(BaseModel):
    __tablename__ = 'record'
    mode = db.Column(db.Integer)
    map_id = db.Column(db.Integer, db.ForeignKey('map.id'), index=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), index=True)
    time = db.Column(db.Integer)
    match_guid = db.Column(db.Text)
    date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Record {self.id}>'


class Map(BaseModel):
    __tablename__ = 'map'
    name = db.Column(db.Text)
    author = db.Column(db.Text)
    workshop_url = db.Column(db.Text)
    records = db.relationship('Record', backref='map', lazy=True)

    def __repr__(self):
        return f'<Map {self.id}>'


# Indices
# db.Index('ix_record_rank_on_map_and_mode',
#          func.rank().over(
#              order_by=Record.time,
#              partition_by=(Record.map_id, Record.mode)
#          ))
