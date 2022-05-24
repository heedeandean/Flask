from distutils.log import debug
from email.mime import application
from venv import create
from photolog import create_app

application = create_app()

if __name__ == '__main__':
    print('starting test server...')
    application.run(host='0.0.0.0', post=5000, debug=True)