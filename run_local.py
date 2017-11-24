"""Run the app locally."""

from qldf import create_app
import os

app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
