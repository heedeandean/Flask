# 로그인 처리 모듈.

from flask import render_template, request, current_app, session, redirect, url_for
from functools import wraps
from werkzeug import check_password_hash
from wtforms import Form, TextField, PasswordField, HiddenField, validators

from photolog.database import dao
from photolog.photolog_logger import Log
from photolog.photolog_blueprint import photolog
from photolog.model.user import User

# 요청이 완료된 후에 DB연결에 사용된 세션을 종료함.
@photolog.teardown_request
def close_db_session(exception=None):
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session_key = \
                request.cookies.get(current_app.config['SESSION_COOKIE_NAME'])
                
            is_login = False
            if session.sid == session_key and session.__contains__('user_info'):
                is_login = True
            
            if not is_login:
                return redirect(url_for('.login_form', next=request.url))

            return f(*args, **kwargs)
        
        except Exception as e:
            Log.error("Photolog error occurs : %s" % str(e))
            raise e
    
    return decorated_function

# 로그인 성공 후 페이지.
@photolog.route('/')
@login_required
def index():
    return redirect(url_for('.show_all'))

# 로그인 화면.
@photolog.route('/user/login')
def login_form():
    next_url = request.args.get('next', '')
    regist_username = request.args.get('regist_username', '')
    update_username = request.args.get('update_username', '')
    Log.info('(%s)next_url is %s' % (request.method, next_url))

    form = LoginForm(request.form)

    return render_template('login.html',
                            next_url=next_url,
                            form=form,
                            regist_username=regist_username,
                            update_username=update_username)

# 로그인 기능.
@photolog.route('/user/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    next_url = form.next_url.data
    login_error = None

    if form.validate():
        session.permanent = True

        username = form.username.data
        password = form.password.data
        next_url = form.next_url.data

        Log.info('(%s)next_url is %s' % (request.method, next_url))

        try:
            user = dao.query(User). \
                   filter_by(username=username). \
                   first()
        
        except Exception as e:
            Log.error(str(e))
            raise e

        if user:
            if not check_password_hash(user.password, password):
                login_error = '잘못된 비밀번호.'
            
            else:
                session['user_info'] = user

                if next_url != '':
                    return redirect(next_url)
                else:
                    return redirect(url_for('.index'))
        else:
            login_error = '사용자가 존재하지 않습니다!'
    
    return render_template('login.html',
                            next_url=next_url,
                            error=login_error,
                            form=form)

# 로그아웃.
@photolog.route('/logout')
@login_required

def logout(): # 세션을 초기화 함.
    session.clear()

    return redirect(url_for('.index'))

# 로그인 화면에서 username & password 입력값 검증.
class LoginForm(Form):
    username = TextField('Username',
                         [validators.Required('사용자명을 입력하세요.'),
                          validators.Length(min=4, max=50,
                                            message='4자리 이상 50자리 이하로 입력하세요.')])
    
    password = PasswordField('New Password',
                             [validators.Required('비밀번호를 입력하세요.'),
                              validators.Length(min=4, max=50,
                                                message='4자리 이상 50자리 이하로 입력하세요.')])

    next_url = HiddenField('Next URL')
