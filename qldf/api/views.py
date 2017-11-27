from flask import jsonify, Blueprint, render_template
from qldf import db
from qldf.models import Map, WorkshopItem
from sqlalchemy import inspect

api = Blueprint('api', __name__, url_prefix='/api/', template_folder='templates')


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@api.route('docs/')
def docs():
    return render_template('docs.html')


@api.route('maps/')
def get_maps():
    rows = db.session.query(Map,
                            WorkshopItem).\
        outerjoin(WorkshopItem).\
        all()
    maps_dict = {row.Map.id: (object_as_dict(row.Map), object_as_dict(row.WorkshopItem) if row.WorkshopItem else None) for row in rows}
    return jsonify(maps_dict)


@api.route('players/')
def get_players():
    pass


@api.route('records/')
def get_records():
    pass
