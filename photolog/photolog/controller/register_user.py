# 사용자 등록 모듈.

import os
from flask import render_template, request, redirect, url_for, session, \
                  current_app, jsonify
from werkzeug import generate_password_hash
from wtforms import Form, TextField, PasswordField, HiddenField, validators

from photolog.photolog_logger import Log
from photolog.photolog_blueprint import photolog
from photolog.database import dao
from photolog.model.user import User
from photolog.controller.login import login_required

@photolog.route('/user/regist')
# 회원가입 폼 제공 함수.
def register_user_form():
    form = RegisterForm(request.form)

    return render_template('regist.html', form=form)

@photolog.route('/user/regist', methods=['POST'])
# 회원가입.
def register_user():
    form = RegisterForm(request.form)

    if form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        try:
            user = User(username, email, generate_password_hash(password))
            dao.add(user)
            dao.commit()

            Log.debug(user)

        except Exception as e:
            error = "DB error occurs : " + str(e)
            Log.error(error)
            dao.rollback()
            raise e

        else:
            # 회원가입이 되면, 로그인 화면으로 이동.
            return redirect(url_for('.login', regist_username=username))
    else:
        return render_template('regist.html', form=form)

@photolog.route('/user/<username>')
@login_required
# 사용자 정보 수정 폼 제공 함수.
def update_user_form(username):
    current_user = __get_user(username)
    form = UpdateForm(request.form, current_user)

    return render_template('regist.html',
                            user=current_user,
                            form=form)

@photolog.route('/user/<username>'. methods=['POST'])
@login_required
# 사용자 정보 수정.
def update_user(username):
    current_user = __get_user(username)
    form = UpdateForm(request.form)

    if form.validate():
        email = form.email.data
        password = form.password.data

        try:
            current_user.email = email
            current_user.password = generate_password_hash(password)
            dao.commit()

        except Exception as e:
            dao.rollback()
            Log.error(str(e))
            raise e

        else:
            # 변경된 사용자 정보를 세션에 반영.
            session['user_info'].email = current_user.email
            session['user_info'].password = current_user.password
            session['user_info'].password_confirm = current_user.password

            # 사용자 정보가 변경되면, 로그인 화면으로 이동.
            return redirect(url_for('.login', update_username=username))
    else:
        return render_template('regist.html', user=current_user, form=form)

def __get_user(username):
    try:
        current_user = dao.query(User).\
                            filter_by(username=username).\
                            first()

        Log.debug(current_user)
        return current_user

    except Exception as e:
        Log.error(str(e))
        raise e

# 회원 탈퇴.
@photolog.route('/user/unregist')
@login_required
def unregist():
    user_id = session['user_info'].id

    try:
        user = dao.query(User).filter_by(id=user_id).first()
        Log.info("unregist:"+user.username)

        if user.id == user_id:
            dao.delete(user)

            # 업로드된 사진 삭제.
            try:
                upload_folder = \
                    os.path.join(current_app.root_path,
                                 current_app.config['UPLOAD_FOLDER'])
                __delete_files(upload_folder, user.username)
            
            except Exception as e:
                Log.error("파일 삭제에 실패했습니다. : %s" + str(e))

            dao.commit()
        
        else:
            Log.error("존재하지 않는 사용자의 탈퇴시도 : %d", user_id)
            raise Exception
    
    except Exception as e:
        Log.error(str(e))
        dao.rollback()
        raise e
    
    return redirect(url_for('.logout'))

def __delete_files(filepath, username):
    import glob

    # 원본 이미지 파일 제거.
    del_filepath_rule = filepath + username + "_*"
    files = glob.glob(del_filepath_rule)
    for f in files:
        Log.debug(f)
        os.remove(f)

    # 썸네일 제거.
    del_filepath_rule = filepath + "thumb_" + username + "_*"
    files = glob.glob(del_filepath_rule)
    for f in files:
        Log.debug(f)
        os.remove(f)

@photolog.route('/user/check_name', methods=['POST'])
def check_name():
    username = request.json['username']
    
    # DB에서 username 중복 확인.
    if __get_user(username):
        return jsonify(result = False)
    else:
        return jsonify(result = True)

# 정보 수정 화면에서 이메일, 비밀번호, 비밀먼호 확인 값을 검증.
class UpdateForm(Form):
    username = TextField('Username')

    email = TextField('Email',
                      [validators.Required('이메일을 입력하세요.'),
                       validators.Email(message='형식에 맞지 않는 이메일입니다.')])

    password = \
        PasswordField('New Password',
                      [validators.Required('비밀번호를 입력하세요.'),
                       validators.Length(min=4, max=50, 
                        message='4자리 이상 50자리 이하로 입력하세요.'),
                       validators.EqualTo('password_confirm',
                                          message='비밀번호가 일치하지 않습니다.')])

    password_confirm = PasswordField('Confirm Password')

# 회원가입 화면에서 사용자명, 이메일, 비밀번호, 비밀먼호 확인 값을 검증.
class RegisterForm(Form):
    username = TextField('Username',
                         [validators.Required('사용자명을 입력하세요.'),
                          validators.Length(min=4, max=50, 
                           message='4자리 이상 50자리 이하로 입력하세요.')])

    email = TextField('Email',
                      [validators.Required('이메일을 입력하세요.'),
                       validators.Email(message='형식에 맞지 않는 이메일입니다.')])

    password = \
        PasswordField('New Password',
                      [validators.Required('비밀번호를 입력하세요.'),
                       validators.Length(min=4, max=50, 
                        message='4자리 이상 50자리 이하로 입력하세요.'),
                       validators.EqualTo('password_confirm',
                                          message='비밀번호가 일치하지 않습니다.')])

    password_confirm = PasswordField('Confirm Password')    

    username_check = \
        HiddenField('Username Check',
                     [validators.Required('사용자명 중복을 확인하세요.')])


