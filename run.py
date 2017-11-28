"""Run the app locally."""

from qldf import create_app
import os
config = os.environ.get('QLDF_CONFIG', 'config.config')
app = create_app(config)

if __name__ == '__main__':
    app.logger.info('running qldf...')
    app.run(debug=app.config['DEBUG'],
            use_reloader=app.config['USE_RELOADER'],
            host=app.config['HOST'],
            port=app.config['PORT'])
