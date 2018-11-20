from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from bluelog.models import Category

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1,128)])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class SettingForm(FlaskForm):
    name = StringField('用户名', validators=[DataRequired(), Length(1, 70)])
    blog_title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('子标题', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('关于', validators=[DataRequired()])
    submit = StringField('提交')

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('类别', coerce=int, default=1)
    body = CKEditorField('博文', validators=[DataRequired()])
    submit = SubmitField('提交')

class CategoryForm(FlaskForm):
    name = StringField('类别', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField('提交')

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('用户已存在')

class CommentForm(FlaskForm):
    author = StringField('姓名', validators=[DataRequired(), Length(1, 30)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 254)])
    site = StringField('网址', validators=[Optional(), URL(), Length(0,255)])
    body = TextAreaField('评论', validators=[DataRequired()])
    submit = SubmitField('提交')

class AdminCommentForm(FlaskForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()

class LinkForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField('提交')