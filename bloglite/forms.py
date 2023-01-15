from flask_wtf import FlaskForm
from wtforms import  StringField,PasswordField,SubmitField,BooleanField,TextAreaField,FileField
from wtforms.validators import  DataRequired ,Length,Email,EqualTo
from flask_wtf.file import FileField, FileAllowed




class LoginForm(FlaskForm):

    username = StringField('Username',validators=[DataRequired(),Length(min=2, max=20)])


    password = PasswordField('Password',validators=[DataRequired()])

    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):

    username = StringField('Username',validators=[DataRequired(),Length(min=2, max=20)])

    name =StringField('Name',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()]
    )

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password =PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')


class UpdateProfileForm(FlaskForm):

    username = StringField('Username',validators=[DataRequired(),Length(min=2, max=20)])

    name =StringField('Name',validators=[DataRequired(),Length(min=2,max=20)])

    email = StringField('Email',validators=[DataRequired(),Email()]
    )
    profile_image =  FileField("Upload Profile Picture",  validators=[FileAllowed(['jpg','jpeg', 'png'])])

    submit = SubmitField('Update')


class BlogForm(FlaskForm):
        title = StringField("Title" ,   validators=[DataRequired()])
        blog_image =  FileField("Add Blog Image",  validators=[FileAllowed(['jpg','jpeg', 'png'])])
        caption = TextAreaField("Caption" , validators= [DataRequired()])
        submit= SubmitField("Add Post")