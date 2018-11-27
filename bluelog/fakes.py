import random

from faker import Faker
from sqlalchemy.exc import IntegrityError
# from bluelog import db
from bluelog.extensions import db
from bluelog.models import Admin, Category, Post, Comment, Link

fake = Faker('zh_CN')


def fake_admin():
    """生成虚拟管理员信息"""
    admin = Admin(
        username='admin',
        blog_title='管理员的博文',
        blog_sub_title="只是，我是虚拟的。",
        name='米玛· 基里戈',
        about='米玛· 基里戈的About...'
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    """生成虚拟博文标签10项"""
    category = Category(name='默认标签')     # 创建默认标签
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())   # 创建虚拟标签
        db.session.add(category)
        try:                                    # 防止出现重复标签名称
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    """生成虚拟博文50篇"""
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),     # 随机标签
            timestamp=fake.date_time_this_year()
        )

        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    """生成虚拟评论500篇"""
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)     # 添加特殊评论 各50条
    for i in range(salt):
        # 添加未审核评论50篇
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,                             # 未审核标记
            post=Post.query.get(random.randint(1, Post.query.count()))      # 随机确定被评论博文
        )
        db.session.add(comment)

        # 添加管理员发表的评论50篇
        comment = Comment(
            author='米玛· 基里戈',
            email='mima@example.com',
            site='example.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,                        # 来自管理员
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))      # 随机确定被评论博文
        )
        db.session.add(comment)
    db.session.commit()

    # 添加已审核的回复50篇
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),    # 随机确定被回复评论
            post=Post.query.get(random.randint(1, Post.query.count()))              # 随机确定被回复博文
        )
        db.session.add(comment)
    db.session.commit()


def fake_links():
    """添加外部链接"""
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    baidu = Link(name='百度', url='https://www.baidu.com/')
    google = Link(name='Google+', url='#')
    db.session.add_all([twitter, facebook, baidu, google])
    db.session.commit()
