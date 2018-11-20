from flask import render_template,flash, redirect,url_for, request, current_app, Blueprint
from flask_login import login_required, current_user
from bluelog.extensions import db
from bluelog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from bluelog.models import Post, Category, Comment, Link
from bluelog.utils import redirect_back

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        pass
