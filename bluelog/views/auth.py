from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from bluelog.forms import LoginForm
from bluelog.models import Admin
from bluelog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('Welcome back.欢迎回来。', 'info')
                return redirect_back()
            flash('Invalid username or password.无效的用户名或密码', 'warning')
        else:
            flash('No account.没有这个用户。', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """退出登录"""
    logout_user()
    flash('Logout success.退出。', 'info')
    return redirect_back()
