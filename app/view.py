from werkzeug.utils import redirect
from app import app
from flask import render_template, redirect, url_for, abort, request, session, flash
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

temp_user = {
   "userid" : "annup76779",
   "password" : "$5$rounds=535000$26.5/F/Kaww15cbx$phnbJlIPXrp2dHVA1izS0PKbcNlxYwUC66.0CEelfg0"
}

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
         if self.form.get("userid", None) == temp_user.get("userid") and sha256_crypt.verify(self.form.get("password"), temp_user.get("password")):
            return True
         else:
            return False
      elif self.type == 2: # ADMIN
         if self.form.get("adminid") == param.get("adminid") and sha256_crypt.verify(self.form.get("adminpass"), param.get("password")):
            return True
         else:
            return False
      else:
         print("Invalid user type")
      return False

# default page of the app
@app.route('/')
def index():
   if session.get("kleen&tidy-contractor-session", None) is not None:
      return redirect("/contractor/home", title="Home | Sub-Contractor")
   else:
      return redirect("/team_login")


#------- general zone starts -------


#about us route
@app.route("/about")
def about():
   return render_template("/general/index.html", title="Home | About Us")

# Sub-contractor's Login route
@app.route('/team_login')
def team_login():
   if session.get("kleen&tidy-contractor-session", None) is not None:
      return redirect("/contractor/home")
   return render_template("/general/team_login.html", title="Login | Contractor")

# team_login submission and authentication process
@app.route("/contractor/authentication", methods=['POST'])
def authenticate_contractor():
   if request.method == "POST":
      auth = Authenticate(request.form)
      if auth.check():
         session["kleen&tidy-contractor-session"] = str(os.urandom(32))
         return redirect("/contractor/home")
      else:
         flash("User Id or Password didn't matched", "danger")
         return redirect("/team_login")
   else:
      abort(405)


#------- general zone ends -------


#------- contrator zone starts -------


# contractor's home page
@app.route("/contractor/home")
def contractor_home():
   if session.get("kleen&tidy-contractor-session", None) is not None:
      return render_template("/contractor/index.html",title="Welcome")
   else:
      flash("Login Required!","warning")
      return redirect("/team_login")


# zxcz





# ----- admin zone started ------


# admin login route
@app.route('/admin_login')
def admin_login():
   if session.get("kleen&tidy-admin-session", None) is not None:
      return redirect("/admin/home")
   return render_template("/admin/admin_login.html")

# admin authentication route
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
      abort(405)

#admin home page (Login Required)
@app.route('/admin/home')
def admin_index():
   if session.get("kleen&tidy-admin-session", None) is not None:
      return render_template("/admin/admin_home.html", title="Admin Home")
   else:
      return redirect("/admin_login")

#route to add jobs by admin (Login required)
@app.route('/admin/add/<obj>')
def add_jobs(obj):
   if session.get("kleen&tidy-admin-session", None) is not None:
      if obj == "jobs":
         return render_template("/admin/add_jobs.html", title="Add Jobs")
      elif obj == "contractor":
         return render_template("/admin/add_contractor.html", title = "Add Sub-Contractor")

   else:
      return redirect("/admin_login")

# Route to save the posted jobs(Login Required)
@app.route("/admin/post/jobs", methods=['POST'])
def post_jobs():
   if session.get("kleen&tidy-admin-session", None) is not None:
      return redirect("/admin/add/jobs")
   else:
      return redirect("/admin_login")

# route to view all the jobs by admin (Login Required)
"""
in this route we are directly delivering the data of any filtered data or empty filter data
but
if user wants to get it by ajax then we have another route /admin/request/jobs/<fiterid>
"""
@app.route("/admin/view/jobs/")
@app.route("/admin/view/jobs/<filter>")
def admin_view_jobs(filter = "1"):
   if session.get("kleen&tidy-admin-session", None) is not None:
      title_dict = {
            "1": "All Jobs", "2":"Jobs Posted Today","3": "Active Jobs", "4":"Completed Jobs", "5":"Reassigned Jobs", "6":"To-do Today"
        }
      return render_template("/admin/view_jobs.html", title=title_dict.get(filter), value = filter)
   else:
      return redirect("/admin_login")

@app.route('/admin/request/jobs/<filterid>')
def request_job(filterid):
   pass


@app.route("/admin/view/contractor/")
@app.route("/admin/view/contractor/<filter>")
def admin_view_contractor(filter = "-1"):
   if session.get("kleen&tidy-admin-session", None) is not None:
      return render_template("/admin/view_contractor.html", title="Contactor's List", value = filter)

@app.route("/admin/open/contractor/<userid>")
def open_contractor(userid):
   if session.get("kleen&tidy-admin-session", None) is not None:
      users = {
         "userid":"annup76779",
         "business/contact":"Anurag Pandey",
         "ABN":"12345678911",
         "mb_no":"+91 8726771497",
         "email":"annup76779@gmail.com",
         "address":"Shakti Nagar, Pure Ishawarnath",
         "jobs":(["67","Glass Clean","Abhinav Srivastava","+91 8726771497","04/04/2021",
         "Hey there you have to clean all the widnow glasses in my building including glasses inside the rooms",
         "Hey there you have to clean all the widnow glasses in my building including glasses inside the rooms",
         "Shakti Nagar, Pure Ishwarnath.",
         "02/04/2021",
         "Completed"
         ],["68","Glass Clean","Dhanya","+91 8726771497","04/04/2021",
         "Hey there you clean the sevage of the area given in address",
         "",
         "Kerela.",
         "02/04/2021",
         "Accepted"
         ])
      }
      if users.get("userid", None) == userid:
         return render_template("/admin/profile.html", title = "Contractor Profile", profile = users, category = [1,11,12], total = sum([1,11,12]))
   else:
      return redirect("/admin_login")

#----- admin zone ended ----------

# logout route
@app.route("/logout/<userType>")
def Logout(userType):
   if userType == "contractor":
      session["kleen&tidy-contractor-session"] = None
   elif userType == "admin":
      session["kleen&tidy-admin-session"] = None 
      return redirect("/admin_login")
   else:
      return redirect("/")