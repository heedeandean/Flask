# photolog 패키지 초기화 모듈.
# Flask 생성.

import os
from flask import Flask, render_template, request, url_for

def print_settings(config):
    print('============================================')
    print('PHOTOLOG APPLICATION 설정.')
    print('============================================')
    for key, value in config:
        print('%s=%s' % (key, value))
    print('============================================')

def not_found(error):
    return render_template('404.html'), 404    

def server_error(error):
    err_msg = str(error)
    return render_template('500.html', err_msg=err_msg), 500

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

def create_app(config_filepath='resource/config.cfg'):
    photolog_app = Flask(__name__)

    from photolog.photolog_config import PhotologConfig
    photolog_app.config.from_object(PhotologConfig)
    photolog_app.config.from_pyfile(config_filepath, silent=True)
    print_settings(photolog_app.config.items())

    # 로그 초기화.
    from photolog.photolog_logger import Log
    log_filepath = os.path.join(photolog_app.root_path,
                                photolog_app.config['LOG_FILE_PATH'])
    Log.init(log_filepath=log_filepath)

    # DB 처리.
    from photolog.database import DBManager
    db_filepath = os.path.join(photolog_app.root_path,
                               photolog_app.config['DB_FILE_PATH'])
    db_url = photolog_app.config['DB_URL'] + db_filepath
    DBManager.init(db_url, eval(photolog_app.config['DB_LOG_FLAG']))
    DBManager.init_db()

    from photolog.controller import login
    from photolog.controller import photo_show
    from photolog.controller import photo_upload
    from photolog.controller import register_user
    from photolog.controller import twitter

    from photolog.photolog_blueprint import photolog
    photolog_app.register_blueprint(photolog)

    # SessionInterface 설정.
    from photolog.cache_session import SimpleCacheSessionInterface
    photolog_app.session_interface = SimpleCacheSessionInterface()

    photolog_app.register_error_handler(404, not_found)
    photolog_app.register_error_handler(500, server_error)

    photolog_app.jinja_env.globals['url_for_other_page'] = \
        url_for_other_page

    return photolog_app
