from app import app
from flask import render_template, redirect, url_for, abort, request, flash
from flask_login import login_user, login_required, current_user, logout_user
from app.modal import Userlogin, is_admin, is_contractor


#------- general zone starts -------


#about us route
@app.route("/about")
def about():
   return render_template("/general/index.html", title="Home | About Us")

# Sub-contractor's Login route
@app.route('/')
def team_login():
   try:
      if current_user.is_authenticated and not is_admin(current_user.id):
         return redirect(url_for("sub_cont.contractor_home"))
      return render_template("/general/team_login.html", title="Login | Contractor")
   except Exception as e:
      flash(e, "error")
      return redirect(request.url)

# team_login submission and authentication processd
@app.route("/contractor/authentication", methods=['POST'])
def authenticate_contractor():
   if request.method == "POST":
      user = Userlogin.query.get(request.form.get("userid", None))
      if user and user.verify_password(request.form.get("password", "")):
         login_user(user)
         return redirect(url_for("sub_cont.contractor_home"))
      else:
         flash("User Id or Password didn't matched", "danger")
         return redirect("/team_login")
   else:
      abort(405)

@app.route("/logout")
def logout():
   if is_admin(current_user.id):
      page = url_for("admin.admin_login")
   else:
      page = url_for("team_login")
   logout_user()
   return redirect(page)
