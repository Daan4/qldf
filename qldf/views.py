from flask import Blueprint, render_template, session, url_for

bp_root = Blueprint('root', __name__, url_prefix='/')


@bp_root.route('/')
def index():
    return 'Hello, World!'


def setup_error_routing(app):
    @app.errorhandler(404)
    def not_found_error(error):
        try:
            redirect_url = session['previous_page']
        except KeyError:
            redirect_url = url_for('root.index')
        return render_template('404.html', title='404', redirect_url=redirect_url), 404

    @app.errorhandler(500)
    def internal_error(error):
        try:
            redirect_url = session['previous_page']
        except KeyError:
            redirect_url = url_for('root.index')
        return render_template('500.html', title='500', redirect_url=redirect_url), 500
