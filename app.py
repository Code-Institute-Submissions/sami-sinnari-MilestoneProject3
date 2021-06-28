# Most of the code I implemented below has been thought by Code Institute.
import os
from flask import Flask, flash, render_template, \
      redirect, request, session, url_for
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


# Routing
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
    mongo.db.recipes.update_one(
        {'_id': ObjectId(recipe_id)}, {'$inc': {'views': int(1)}})
    return render_template("/recipe.html", recipe=recipe_db)


# Sign Up
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

        # Place user into a session cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful! You can now share your own recipes!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one({"username": request.form.get(
            "username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome,{}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password ")
            return redirect(url_for("login"))

    return render_template("/login.html")


# Logout
@ app.route("/logout")
def logout():
    flash("You have been logged out")
    session.clear()
    return redirect(url_for("login"))


# User's Profile
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


# Add Recipe
@ app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if not session.get("user"):
        render_template("templates/error404.html")

    if request.method == "POST":
        is_vegetarian = "on" if request.form.get("is_vegetarian") else "off"
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "category_name": request.form.get("category_name"),
            "img_url": request.form.get("img_url"),
            "cooks_in": request.form.get("cooks_in"),
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


# Edit Recipe
@ app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    if not session.get("user"):
        return render_template("templates/error404.html")

    if session.get("user") != recipe.get("added_by"):
        return redirect(url_for("profile", username=session['user']))

    if request.method == "POST":
        is_vegetarian = "on" if request.form.get("is_vegetarian") else "off"
        submit = {
            "recipe_name": request.form.get("recipe_name"),
            "category_name": request.form.get("category_name"),
            "img_url": request.form.get("img_url"),
            "cooks_in": request.form.get("cooks_in"),
            "recipe_ingredients": request.form.get("recipe_ingredients"),
            "recipe_method": request.form.get("recipe_method"),
            "is_vegetarian": is_vegetarian,
            "added_by": session["user"]
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe successfully edited")
        return redirect(url_for("profile", username=session['user']))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort(
        "category_name", 1)
    return render_template(
        "/edit_recipe.html", recipe=recipe, categories=categories)


# Recipe category
@app.route("/recipe_category/<id>")
def recipe_category(id):
    recipes = list(mongo.db.recipes.find({"category_name": id}))
    return render_template("/recipes.html", recipes=recipes)


# Delete Recipe
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash("Recipe has been Successfully Deleted")
    return redirect(url_for("profile", username=session['user']))


# Search
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    if len(recipes) == 0:
        flash(f"Sorry, there are no recipes under name {query} :( ")
    else:
        flash(f"We found {len(recipes)} result(s) :)")
    return render_template("recipes.html", recipes=recipes)


# Errors
# Code below for errors has been thought here :
# https://flask.palletsprojects.com/en/1.1.x/errorhandling/

@app.errorhandler(403)
def forbidden(e):
    return render_template("/error403.html"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("/error404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("/error500.html"), 500


# Main
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
