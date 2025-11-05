from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class LogForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('内容', validators=[DataRequired()])
    tags = StringField('标签 (用逗号分隔)', validators=[Length(max=200)])
    submit = SubmitField('保存')


class SearchForm(FlaskForm):
    query = StringField('搜索', validators=[Length(max=100)])
    submit = SubmitField('搜索')
