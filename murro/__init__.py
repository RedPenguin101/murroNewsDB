import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY = 'dev',
            DATABASE = os.path.join(app.instance_path, 'murro.sqlite'),
        )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/test_up')
    def test_up():
        return 'server seems to be up'

    # Blueprint imports go here
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import story
    app.register_blueprint(story.bp)
    app.add_url_rule('/', endpoint='index')
    #


    return app
