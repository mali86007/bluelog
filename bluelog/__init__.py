import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

from bluelog.views.admin import admin_bp
from bluelog.views.auth import auth_bp
from bluelog.views.blog import blog_bp
from bluelog.extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment, toolbar, migrate
from bluelog.models import Admin, Post, Category, Comment, Link
from bluelog.settings import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')  # 默认为开发版本

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_shell_context(app)
    register_template_context(app)
    register_request_handlers(app)
    return app


def register_logging(app):
    """注册日志"""
    class RequestFormatter(logging.Formatter):
        """请求格式类"""

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )       # asctiome打印日志的时间 remote_addr

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   # 创立日志格式实例

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/bluelog.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)       # 创立远程日志文件句柄
    file_handler.setFormatter(formatter)        # 远程日志文件句柄格式
    file_handler.setLevel(logging.INFO)         # 远程日志文件级别

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['ADMIN_EMAIL'],
        subject='Bluelog Application Error',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))     # 创立远程邮件日志句柄
    mail_handler.setLevel(logging.ERROR)            # 远程邮件日志级别
    mail_handler.setFormatter(request_formatter)    # 远程邮件日志格式为自定义格式request_formatter

    if not app.debug:
        app.logger.addHandler(mail_handler)     # 添加句柄，下同
        app.logger.addHandler(file_handler)


def register_extensions(app):
    """注册扩展模块"""
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    """注册蓝本"""
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):
    """注册命令行上下文"""
    @app.shell_context_processor
    def make_shell_context():
        """制造命令行上下文，返回词典"""
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)


def register_template_context(app):
    """注册模板上下文"""
    @app.context_processor
    def make_template_context():
        """制造模板上下文，返回词典"""
        admin = Admin.query.first()                                 # 当前管理员
        categories = Category.query.order_by(Category.name).all()   # 博文分类集
        links = Link.query.order_by(Link.name).all()                # 外部链接集
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()       # 未审核评论数
        else:
            unread_comments = None
        return dict(
            admin=admin, categories=categories,
            links=links, unread_comments=unread_comments)


def register_errors(app):
    """注册错误模块"""
    @app.errorhandler(400)
    def bad_request(e):
        """错误请求400"""
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        """网页未发现404"""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """内部服务器端错误500"""
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """句柄跨域攻击错误"""
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    """注册命令行"""
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.删除后创建')
    def initdb(drop):
        """初始化数据库"""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?将删除数据库，继续？', abort=True)
            db.drop_all()
            click.echo('Drop tables.删除表格')
        db.create_all()
        click.echo('Initialized database.数据库初始化完成。')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.用当前用户名登录')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.用当前密码登录')
    def init(username, password):
        """创建博客"""

        click.echo('Initializing the database...初始化数据库')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...当前管理员已存在')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...创建虚拟系统管理员')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...创建默认分类')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.分类数量，默认10个')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.博文数量，默认50篇')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.评论数量，莫问500篇')
    def forge(category, post, comment):
        """生成虚拟数据"""
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...（生成系统管理员）')
        fake_admin()

        click.echo('Generating %d categories...（生成博文分类）' % category)
        fake_categories(category)

        click.echo('Generating %d posts...（生成博文）' % post)
        fake_posts(post)

        click.echo('Generating %d comments...（生成评论）' % comment)
        fake_comments(comment)

        click.echo('Generating links...（生成外部链接）')
        fake_links()

        click.echo('Done.（生成虚拟数据完成。）')


def register_request_handlers(app):
    """注册请求句柄"""
    @app.after_request
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= app.config['BLUELOG_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: %fs\n Context: %s\nQuery: %s\n '
                    % (q.duration, q.context, q.statement)
                )
        return response
