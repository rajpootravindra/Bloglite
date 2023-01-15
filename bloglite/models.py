from flask_login import  UserMixin,LoginManager
from datetime import datetime
from sqlalchemy.sql import func
from flask_sqlalchemy import  SQLAlchemy

login_manager=LoginManager()
db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
           # Follower Table  Section


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


            # User Table  Section


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_image = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    blogs = db.relationship('Blog', backref='author', passive_deletes=True)
    comments = db.relationship('Comment', backref='author', passive_deletes=True)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


            # Blog Table  Section


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    blog_image = db.Column(db.String(20),nullable=False,default='default_blog.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    caption = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='blog', passive_deletes=True)
    likes = db.relationship('Like',       backref='blog', passive_deletes=True)


    def __repr__(self):
        return f"Blog('{self.title}','{self.caption}', '{self.date_posted}')"


             # omment Table  Section


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id', ondelete="CASCADE"), nullable=False)

             #  Like Table  Section

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id', ondelete="CASCADE"), nullable=False)
    author = db.relationship('User',backref='likes' )








