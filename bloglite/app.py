from flask import Flask,render_template, redirect,request, flash,url_for, abort
from bloglite.forms import LoginForm, RegistrationForm, UpdateProfileForm, BlogForm
import os
import secrets
from PIL import Image
from flask_bcrypt import Bcrypt
from bloglite.models import User,Blog,Like,Comment,db
from flask_login import  login_user, current_user, logout_user, login_required
from bloglite.models import login_manager

            # Initialisation of app

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bloglite.db'
db.init_app(app)
with app.app_context():
    db.create_all()
bcrypt = Bcrypt(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


            # Routes of application

@app.route('/')
@app.route('/home')
@login_required
def home():
    following = [u.id for u in current_user.followed]
    following.append(current_user.id)
    blogs = Blog.query.filter(Blog.user_id.in_(following)).order_by(
        Blog.date_posted.desc())
    for p in blogs:
        p.liked=False
        likes  = [x.user_id for x in p.likes]
        if current_user.id in likes:
            p.liked = True
    return render_template ('home.html', blogs=blogs)
@app.route('/login', methods=['GET', 'POST'])
def login():
      # here will use the current_user() function to redirect him to home page if he is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        # first check if the username id is already in the database or not.
        user = User.query.filter_by(username=form.username.data).first()
        # now if the username is there. then check for the password entered by the user matches with the password in the database table.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            #  so if the username and password is correct , we will use the inbuilt function ,
            # login_user() which we will have to import from the flask_login library/package. to make the login
            # successful

            # second argument is True or False. (remember me)
            login_user(user, remember=form.remember_me.data)
            # after successful login . lets redirect them to the next page. that is home page.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            # if the email and password is incorrect , login will be Unsuccessful,
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template ('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
     if current_user.is_authenticated:
        return redirect(url_for('home'))
     form=RegistrationForm()
     if form.validate_on_submit():
        # <===generating a hash code for the password entered by the  new user===>
        hashed_pass= bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')

        # geting  the information about the new user from the html form(Registrationform)

        new_user = User(username=form.username.data,name=form.name.data,email=form.email.data,password=hashed_pass)

         # adding  this user to the database
        db.session.add(new_user)
        # making change permanent
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        # sending  registered user  to  login page
        return redirect(url_for('login'))


     return render_template ('register.html', form=form)


@app.route("/logout")
@login_required
def logout():
    # inbuilt function called as logout_user() from the flask_login package.
    logout_user()
    return redirect(url_for('home'))

# function to save the blog image.
def save_blog_image(uploaded_image):
    # change the name of the image to a simple name as soon as they will upload a image. this can be done by importing secrets module at the top from python directly , by writing.    import secrets. and using it here.
    random_hex = secrets.token_hex(8)
    # now we will use the os moduel from python to save the file in the same extentions as the image extention. so impor os library and use the function.
    # this function returns 2 values image file without the extension and second is the extension itself.
    # we dont require the file name in this line so we put it as _ underscore.
    _, f_ext = os.path.splitext(uploaded_image.filename)
    # f_name , f_ext = os.path.splitext(form_picture.filename)
    # we need the file name in this next line.
    image_renamed = random_hex + f_ext
    # now we will store this image uploaded into the static folders profile_pics folder.
    picture_path = os.path.join(app.root_path, "static/blog_images", image_renamed)
    # now we will save that picture using the form_picture variable using the save() function. at the picture path that we just created.
    # resize the image before saving.
    output_size = (300, 400)
    # get the image from the form.
    i = Image.open(uploaded_image)
    # now set the thumbnail of the image to the output_size which we have choosen.
    i.thumbnail(output_size)
    # now save this i resized image. into the folder location.
    i.save(picture_path)
    # finally we will return the pictures file name, which was uploaded by the user.
    return image_renamed

# now make an instance of the PostForm class inside the route.py file  inside the new_post() method or route and send it to the create_post.html page. as a variable. also mention the allowed methods for this route, POSt and GET

# function to create new post / add new post

@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def create_blog():
    form=BlogForm()
    if form.validate_on_submit():
        picture_file = 'default_blog.jpeg'
        if form.blog_image.data:
            picture_file = save_blog_image(form.blog_image.data)

        new_blog = Blog(title=form.title.data,blog_image=picture_file, caption=form.caption.data,author= current_user)
        db.session.add(new_blog)
        db.session.commit()
        flash('Your blog has been created!', 'success')
        return redirect(url_for('home'))
    return render_template ('create_blog.html',form=form,title='Create New Blog',legend='Create New blog')
# now we will make a route, to show the specific post , by fetching it by its id.
# fetching the post by its id.

@app.route("/blog/<int:blog_id>")
def blog(blog_id):
    # we can get the post by its id using the get() function.
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog.html', blog=blog)



@app.route("/blog/<int:blog_id>/update", methods=['GET', 'POST'])
# we have to logged in to update the post so we need the login_required decorator
@login_required
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    # we have to make sure the person who wrote the post only should get to update it. not any one else.
    if blog.author != current_user:
        abort(403)        # import the about() function from flask library.
    # now to show the update form. from where we can update the title and content of the post.
    form = BlogForm()
    # if the form is successfully validated on clicking the submit button.
    if form.validate_on_submit():
        if form.blog_image.data:
            picture_file = save_blog_image(form.blog_image.data)
            blog.blog_image = picture_file
        blog.title = form.title.data
        blog.caption = form.caption.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        # after successful update we will redirect the user to the udated  post page.
        # blog_image = url_for("static" , filename = "blog_images/" + current_user.blog.blog_image)
        return redirect(url_for('blog', blog_id = blog_id))
    elif request.method == 'GET':
        # this fetches the blog alredy in the database, which we will get it from method GET
        form.title.data = blog.title
        form.caption.data = blog.caption
        form.blog_image.data = blog.blog_image
    return render_template('create_blog.html', title='Update Blog',
                           form=form, legend='Update Blog')


@app.route("/blog/<int:blog_id>/delete", methods=['POST'])
@login_required
def delete_blog(blog_id):
    # deleting the post by its post_id.
    blog = Blog.query.get_or_404(blog_id)
    # only the person who wrote the post gets to delete it.
    if blog.author != current_user:
        # this will show forbidden message if the post doesnt belong to the user. who wrote the post.
        abort(403)
    db.session.delete(blog)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    # after successfull deletion make the user come to the home page.
    return redirect(url_for('home'))


def save_profile_image(uploaded_image):
    # change the name of the image to a simple name as soon as they will upload a image. this can be done by importing secrets module at the top from python directly , by writing.    import secrets. and using it here.
    random_hex = secrets.token_hex(8)
    # now we will use the os moduel from python to save the file in the same extentions as the image extention. so impor os library and use the function.
    # this function returns 2 values image file without the extension and second is the extension itself.
    # we dont require the file name in this line so we put it as _ underscore.
    _, f_ext = os.path.splitext(uploaded_image.filename)
    # f_name , f_ext = os.path.splitext(form_picture.filename)
    # we need the file name in this next line.
    profile_image_changed = random_hex + f_ext
    # now we will store this image uploaded into the static folders profile_pics folder.
    picture_path = os.path.join(
        app.root_path, "static/profile_images",profile_image_changed )
    # now we will save that picture using the form_picture variable using the save() function. at the picture path that we just created.
    # resize the image before saving.
    output_size = (125, 125)
    # get the image from the form.
    i = Image.open(uploaded_image)
    # now set the thumbnail of the image to the output_size which we have choosen.
    i.thumbnail(output_size)
    # now save this i resized image. into the folder location.
    i.save(picture_path)
    # finally we will return the pictures file name, which was uploaded by the user.
    return profile_image_changed



@app.route('/profile/<string:username>', methods=['POST', 'GET'])
@login_required
def profile(username):
     # make the instance of the UpdateAccountForm and pass that form into the account.html template.
    form =UpdateProfileForm()
    # check if the form is valid on submission .
    if form.validate_on_submit():
        if form.profile_image.data:
            picture_file = save_profile_image(form.profile_image.data)
            current_user.profile_image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data

        db.session.commit()
        flash("Your account details were successfully updated.", "success")
        # after updation we will redirect them to the profile page.
        return redirect(url_for("profile",username=username))
    elif request.method == "GET":
        # this is to populate the form by the current users data as soon as they come to the profile update page.
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.email.data = current_user.email
    following = len(current_user.followed)
    followers = len(current_user.followers)
    follows=username in [u.username for u in current_user.followed]
    user = User.query.filter_by(username=username).first_or_404()
    blogs=Blog.query.filter_by(author=user).all()
    total=len(blogs)
    image_file = url_for(
        "static", filename="profile_images/" + current_user.profile_image)
    # pass this image_file variable into the profile.html template
    return render_template ('profile.html', form=form, image_file=image_file,blogs=blogs,followers=followers,following=following, total=total,user=user,follows=follows
    )


@app.route('/search',methods=['POST'])
@login_required
def search():
    query = request.form.get('search')
    similar_users=User.query.filter(User.username.like(f"{query}%")).all()
    return render_template('search.html',users=similar_users)

@app.route("/following")
def following():
    users =current_user.followed
    # get all the users from the database.
    return render_template('following.html', users=users)


@app.route("/followers")
def followers():
    # get all the users from the database.
    users = User.query.order_by(
        User.username.asc())
    return render_template('followers.html', users=users)


# Function to follow other users

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    current_user.followed.append(user)
    db.session.commit()
    flash('You are now following ' + username + '!')
    return redirect(url_for('profile', username=username))



# Function to unfollow other users

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    current_user.followed.remove(user)
    db.session.commit()
    return  redirect(url_for('profile', username=username))

@app.route("/like/<blog_id>")
def like(blog_id):
    blog = Blog.query.filter_by(id=blog_id).first()
    like = Like.query.filter_by(user_id=current_user.id, blog_id = blog.id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, blog_id=blog.id)
        db.session.add(like)
        db.session.commit()
    return f'{len(blog.likes)}'






