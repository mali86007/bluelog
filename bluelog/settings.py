import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class  BaseConfig(object):
    """基础设置类"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')             # 密钥
    DEBUG_TB_INTERCEPT_REDIRETS = True                         # 调试，默认False
    SQLALCHEMY_TRACK_MODIFICATIONS = False                      # 数据库
    SQLALCHEMY_RECORD_QUERIES = True                            # 数据库

    MAIL_SERVER = os.getenv('MAIL_SERVER')                      # 邮件服务器
    MAIL_PORT = 465                                             # 端口
    MAIL_USE_SSL = True                                         # SSL加密
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')                  # 邮箱用户名
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')                  # 邮箱用户密码
    MAIL_DEFAULT_SENDER = ('Bluelog Admin', MAIL_USERNAME)      # 邮箱默认发送者

    BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')                  # 博客邮箱
    BLUELOG_POST_PER_PAGE = 10                                  # 每页博文
    BLUELOG_MANAGE_POST_PER_PAGE = 15                           # 每页博文（管理）
    BLUELOG_COMMENT_PER_PAGE = 15                               # 每页评论
    BLUELOG_THEMES = {'perfect_blue': 'perfect blue', 'black_swan': 'black Swan'}       # 博客主题
    BLUELOG_SLOW_QUERY_THRESHOLD = 1                            # 查询阈值？


class DevelopmentConfig(BaseConfig):
    """开发设置类"""
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')     # 开发数据库路径


class TestingConfig(BaseConfig):
    """测试设置类"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'      # 测试数据库（内存）


class ProductionConfig(BaseConfig):
    """生产设置类"""
    # SQLALCHEMY_DATABASE_URI = os.path('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))    # 生产数据库路径
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}