from qldf import db
from flask import flash
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import UnmappedInstanceError


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
    name = db.Column(db.Text, nullable=False)
    steam_id = db.Column(db.Text, unique=True, nullable=False)
    records = db.relationship('Record', backref='player', lazy=True)

    def __repr__(self):
        return f'<Player {self.id}>'


class Record(BaseModel):
    __tablename__ = 'record'
    mode = db.Column(db.Integer, nullable=False)
    map_id = db.Column(db.Integer, db.ForeignKey('map.id'), index=True, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), index=True, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    match_guid = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Record {self.id}>'


class Map(BaseModel):
    __tablename__ = 'map'
    name = db.Column(db.Text, nullable=False)
    records = db.relationship('Record', backref='map', lazy=True)
    workshop_item_id = db.Column(db.Integer, db.ForeignKey('workshop_item.id'), index=True)

    def __repr__(self):
        return f'<Map {self.id}>'


class WorkshopItem(BaseModel):
    __tablename__ = 'workshop_item'
    item_id = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text)
    author_steam_id = db.Column(db.Text)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    size = db.Column(db.Float)
    num_comments = db.Column(db.Integer)
    score = db.Column(db.Integer)
    num_scores = db.Column(db.Integer)
    preview_url = db.Column(db.Text)
    maps = db.relationship('Map', backref='workshop_item', lazy=True)

    def __repr__(self):
        return f'<WorkshopItem {self.id}>'
