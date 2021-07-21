import os
from flask import jsonify, request, Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# MySQL connection setting
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD")
MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_PORT=os.getenv("MYSQL_PORT")
MYSQL_DB=os.getenv("MYSQL_DB")

#app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root:my-secret-pw@127.0.0.1:3306/user"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(30), nullable=False)
    job_title = db.Column(
        db.String(30), nullable=False)
    email = db.Column(
        db.String(255), unique=True, nullable=True)
    mobile = db.Column(
        db.String(10), unique=True, nullable=True)
    insert_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(
        db.DateTime, onupdate=datetime.now, default=datetime.now)

    def to_dict(self):
        dictionary = {}
        dictionary["name"] = getattr(self, "name")
        dictionary["job_title"] = getattr(self, "job_title")
        dictionary["communicate_information"] = { 
            "email": getattr(self, "email"),
            "mobile": getattr(self, "mobile")
        }
        return dictionary

@app.route("/")
def index():
    return "This is an API to manage users table."

@app.route("/all_users")
def get_all_user():
    """Function to retrieve all users from the MySQL database"""
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append(user.to_dict())
    return jsonify(data=users_list)

@app.route("/user/<int:uid>", methods=["GET"])
def get_user(uid):
    """Function to get information of a specific user in the MSQL database"""
    user = User.query.filter_by(uid=uid).first()
    if user:
        return jsonify(data=user.to_dict())
    else:
        return jsonify(error="User was not found."), 404

@app.route("/create", methods=["POST"])
def add_user():
    """Function to create a user to the MySQL database"""
    try:
        json = request.json
        user = User(
            name = json["name"],
            job_title = json["job_title"],
            email = json["email"],
            mobile = json["mobile"]
        )
    except:
        return jsonify(error="Please check the data format."), 405
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(response="User was created successfully!")
    except:
        db.session.rollback()
        return jsonify(error="Something wrong happened."), 500
    

@app.route("/update-user/<int:uid>", methods=["PATCH"])
def update_user(uid):
    """Function to update a user in the MYSQL database"""
    try:
        json = request.json
        job_title = json["job_title"]
        email = json["email"]
        mobile = json["mobile"]
    except:
        return jsonify(error="Please check the data format."), 405
    
    user = User.query.filter_by(uid=uid).first()
    if user:
        user.job_title = job_title
        user.email = email
        user.mobile = mobile
        try:
            db.session.commit()
            return jsonify(response="User was updated successfully."), 200
        except:
            db.session.rollback()
            return jsonify(error="Something wrong happened."), 500
    else:
        return jsonify(error="User was not found."), 404



@app.route("/delete/<int:uid>", methods=["DELETE"])
def delete_user(uid):
    """Function to delete a user from the MySQL database"""
    api_key = request.args.get("api_key")
    if api_key == "ForSecurity":
        user = User.query.filter_by(uid=uid).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify(response="User was deleted successfully."), 200
        else:
            return jsonify(error="User was not found."), 404
    else:
        return jsonify(error="You are not allow to delete user."), 403


if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0")