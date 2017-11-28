"""Flask-WTForms forms"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    name = 'search'
    search_string = TextAreaField('Search by player/map name', validators=[DataRequired()])
    search = SubmitField('SEARCH')
