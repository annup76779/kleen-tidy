from werkzeug.utils import redirect
from app import app
from flask import render_template, redirect, url_for, abort, request, session
import os
from passlib.hash import sha256_crypt
import json
# sha256_crypt.hash(value)
# admin-session name => kleen&tidy-admin-session
# contractor session name => kleen&tidy-contractor-session

# function to get the exact path of any file in app
def get_path(file):
    path = os.path.dirname(__file__)
    return os.path.join(path, str(file))

# loading JSON file - config.json
with open(get_path("config.json"), "r") as f:
   param = json.load(f) #json values are loaded and saved in python dictionary param


# class to check authenticate user
class Authenticate:
   def __init__(self, form, user_type = 1):
      self.form = form
      self.type = user_type

   def check(self):
      """
      matches the userid and password transfered to this class by the user of any type with 
      ids and passwords present in that user's datastore.
      user_type => 1: Sub-Contractor
      user_type => 2: Admin(Main Contractor)
      If both the values(id and password) matches
      Returns: True - matched
               False- not matched
      """
      if self.type == 1: # SUB-CONTRACTOR
         pass
      elif self.type == 2: # ADMIN
         if self.form.get("adminid") == param.get("adminid") and sha256_crypt.verify(self.form.get("adminpass"), param.get("password")):
            return True
         else:
            return False
      else:
         print("Invalid user type")
      return False

@app.route('/')
def index():
   return redirect('/admin_login')

"""Here will be sub-contractor's routes"""


@app.route('/admin_login')
def admin_login():
   return render_template("/admin/admin_login.html")

@app.route('/admin/authenticate', methods=['POST'])
def authenticate_admin():
   #testing the type of request form the user
   if request.method == "POST":
      auth = Authenticate(form = request.form, user_type = 2)
      if auth.check():
         session["kleen&tidy-admin-session"] = str(os.urandom(32))
         return redirect("/admin/home")
      else:
         session["session"] = None
         return redirect("/")
   else:
      abort(401)


@app.route('/admin/home')
def admin_index():
   if session.get("kleen&tidy-admin-session", None) is not None:
      return render_template("/admin/admin_home.html", title="Admin Home")
   else:
      return redirect("/admin_login")

@app.route('/admin/add/jobs')
def add_jobs():
   if session.get("kleen&tidy-admin-session", None) is not None:
      return render_template("/admin/add_jobs.html", title="Add Jobs")
   else:
      return redirect("/admin_login")