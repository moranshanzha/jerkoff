from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class ResourceForm(FlaskForm):
    file = FileField('文件', validators=[
        FileRequired(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'obj', 'fbx'], '只允许上传图片和3D模型文件')
    ])
    file_type = SelectField('类型', choices=[('skin', '皮肤'), ('model', '模型')], validators=[DataRequired()])
    description = TextAreaField('描述', validators=[Length(max=200)])
    submit = SubmitField('上传')


class SearchResourceForm(FlaskForm):
    query = StringField('搜索', validators=[Length(max=100)])
    submit = SubmitField('搜索')
