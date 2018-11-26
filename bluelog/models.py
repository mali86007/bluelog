from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bluelog.extensions import db

class Admin(db.Model, UserMixin):
    """管理员类数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))             #
    password_hash = db.Column(db.String(128))       # 密码散列值
    blog_title = db.Column(db.String(60))           # 博客标题
    blog_sub_title = db.Column(db.String(100))      # 博客副标题
    name = db.Column(db.String(30))                 # 用户姓名
    about = db.Column(db.Text)                      # 关于信息

    def set_password(self, password):
        """密码处理后返回哈希值赋值给密码散列值字段"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """将接收到的密码用密码散列值校验"""
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    """博文标签数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)                # 博文标签名称，不得重复
    posts = db.relationship('Post', back_populates='category')  # 按标签分类博文集，反向引用category建立双向关系

    def delete(self):
        """删除分类"""
        default_category = Category.query.get(1)    # 返回id=1的记录 ？万一没有id=1的分类值哪？
        posts = self.posts[:]                       # 返回当前博文集
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()

class Post(db.Model):
    """博文类数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))                # 标题
    body = db.Column(db.Text)                       # 博文正文
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)     # 博文时间戳
    can_comment = db.Column(db.Boolean, default=True)                           # 可否评论，默认可
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))           # 标签id
    category = db.relationship('Category', back_populates='posts')              # 对博文标签的反向引用关系
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')      # 对评论的反向引用关系

class Comment(db.Model):
    """评论类（附加回复）数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))               # 作者
    email = db.Column(db.String(254))               # 作者电子邮件
    site = db.Column(db.String(255))                # 作者站点
    body = db.Column(db.Text)                       # 评论正文
    from_admin = db.Column(db.Boolean, default=False)       # 是否来自管理员，默认不是
    reviewed = db.Column(db.Boolean, default=False)         # 是否通过审核，默认未通过
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)     # 评论时间戳
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))             # 指向自身的id字段
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))                   # Post外键
    post = db.relationship('Post', back_populates='comments')                   # 与Comment的关系
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')    # 对评论的回复集
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])    # 定义id为远程端，replied_id为本地端

class Link(db.Model):
    """外部链接类数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))