import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)



#### Index and route  #####


@app.route("/")
def get_index():
    toprecipes = mongo.db.recipes.find()
    return render_template("index.html", recipes=toprecipes)

    
@app.route("/get_recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


# One recipe
@app.route("/recipe/<recipe_id>")
def recipe(recipe_id):
    recipe_db = mongo.db.recipes.find_one_or_404({'_id': ObjectId(recipe_id)})
    mongo.db.recipes.update({'_id': ObjectId(recipe_id)}, {'$inc': {'views': int(1)}})
    return render_template("/recipe.html", recipe=recipe_db)

#### Sign Up #### 

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")

    return render_template("register.html")

#### Login #### 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect( url_for("profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password ")
            return redirect(url_for("login"))

    return render_template("/login.html")

#### Logout #### 

@ app.route("/logout")
def logout():
    flash("You have been logged out")
    session.clear()
    return redirect(url_for("login"))


#### User's Profile ####

@ app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    user = session.get("user").lower()
    user_recipes = list(
        mongo.db.recipes.find({"added_by": session["user"]}))
    if user is not None:
        return render_template(
            "profile.html", username=username, recipes=user_recipes)
    else:
        return render_template("/login.html")


#### Add the recipe ####

@ app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if not session.get("user"):
        render_template("templates/404.html")

    if request.method == "POST":
        is_vegetarian = "on" if request.form.get("is_vegetarian") else "off"
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "category_name": request.form.get("category_name"),
            "img_url": request.form.get("img_url"),
            "prep_time": request.form.get("prep_time"),
            "recipe_ingredients": request.form.get("recipe_ingredients"),
            "recipe_method": request.form.get("recipe_method"),
            "is_vegetarian": is_vegetarian,
            "added_by": session["user"]
        }

        mongo.db.recipes.insert_one(recipe)
        flash("Recipe added successfully")
        return redirect(url_for("profile", username=session['user']))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "add_recipe.html", categories=categories
        )

#### Comments ####

@app.route('/comments', methods=['POST'])
def comments():
    if request.method == 'POST':
        comment = {
            'person_name': request.form.get('person_name'),
            'user_comment': request.form.get('user_comment')
        }

        mongo.db.comments.insert_one(comment)
        flash('Comment posted successfully')
        return redirect(url_for(""))

    return render_template( "comment.html")
    
    #return redirect(url_for('comments', comments_id=request.form.get('comments_id')))
####  Main  #####
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)