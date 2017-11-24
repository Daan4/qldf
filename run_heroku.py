"""Runs the app after being deployed on Heroku."""

from qldf import create_app
import os

app = create_app('config.heroku_config')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=int(os.environ.get('PORT', 5000)), host='0.0.0.0')
