"""
    photolog.controller.photo_show
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    업로드된 사진을 보여준다.
"""
import os
from flask import request, current_app, send_from_directory, \
                  render_template, session, url_for
from sqlalchemy import or_

from photolog.database import dao
from photolog.model.photo import Photo
from photolog.controller.login import login_required
from photolog.photolog_blueprint import photolog
from photolog.photolog_logger import Log

# 파일 사이즈를 읽기 편한 포맷으로 변경해 주는 함수.
def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

# 업로드된 사진 정보를 얻는 함수.
def get_photo_info(photolog_id):
    photo = dao.query
