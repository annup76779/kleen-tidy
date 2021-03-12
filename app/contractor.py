from flask import Blueprint, render_template, redirect, url_for, abort, request, jsonify, flash
from flask_login import login_required, current_user, logout_user
from app.modal import is_contractor, Status, db, Jobs, datetime, get_upcomming_seven_day_jobs

sub_cont = Blueprint("sub_cont", __name__, url_prefix="/contractor")

#------- contrator zone starts -------

# contractor's home page
@sub_cont.route("/home")
@login_required
def contractor_home():
   if is_contractor(current_user.id):
      return render_template("/contractor/index.html",title="Welcome", userid = current_user.id)
   else:
      logout_user()
      flash("Please login!", "danger")
      return redirect(url_for("team_login"))

# contractor's job view page
@sub_cont.route("/jobs")
@login_required
def jobs():
   if is_contractor(current_user.id):
      return render_template("/contractor/jobs.html",title = "Contractor | Jobs", userid = current_user.id)
   else:
      logout_user()
      flash("Please login!", "danger")
      return redirect(url_for("team_login"))

# contractor view <filter> jobs Route
@sub_cont.route('/view/jobs/<filter>')
@login_required
def view_jobs(filter):
   if is_contractor(current_user.id):
      try:
         if filter == "1":
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.status == 0).all()
            return render_template("/contractor/filter_jobs.html",title="New Jobs", filter = filter, jobs = jobs, userid = current_user.id)
         elif filter == "2":
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.status == 1, Status.userid == current_user.id).all()
            return render_template("/contractor/filter_jobs.html",title="Active Jobs", filter = filter, jobs = jobs, userid = current_user.id)

         elif filter == "3":
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.status == 2, Status.userid == current_user.id).all()
            return render_template("/contractor/filter_jobs.html",title="Completed Jobs", filter = filter, jobs = jobs, userid = current_user.id)

         elif filter == "4":
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.status == 3, Status.userid == current_user.id).all()
            return render_template("/contractor/filter_jobs.html",title="Reassigned Jobs", filter = filter, jobs = jobs, userid = current_user.id)

         elif filter == "5":
            jobs = get_upcomming_seven_day_jobs(current_user.id)
            return render_template("/contractor/filter_jobs.html",title="Schedule", filter = filter, jobs = jobs, userid = current_user.id)
      except Exception as e:
         flash(f"Error Occurred: {e}", "danger")
         return render_template("/contractor/filter_jobs.html",title="View Jobs", filter = filter, userid = current_user.id)
   else:
      logout_user()
      flash("Please login!", "danger")
      return redirect(url_for("team_login"))


@sub_cont.route("/accept/job/<id>")
@login_required
def accept(id):
   if is_contractor(current_user.id):
      job = Status.query.filter_by(jobid = id, status = 0).first()
      if job:
         job.status = 1
         job.userid = current_user.id
         db.session.add(job)
         db.session.commit()
         return jsonify({"status":True,"message":"Accepted <i class='fa fa-check'></i>"})
      else:
         return jsonify({"status":False, "id":f"job{id}","message":"<span class='text-danger'>Unable to accept the job</span>"})
   else:
      logout_user()
      return redirect(url_for("admin.admin_login"))

@sub_cont.route("/finished/job/<id>")
@login_required
def finish(id):
   if is_contractor(current_user.id):
      job = Status.query.filter_by(jobid = id, userid = current_user.id).first()
      if job and job.status == 1 or job.status == 3:
         job.status = 2
         date_time = datetime.now()
         end_date = date_time.strftime("%d-%m-%Y   %X")
         job.end_date = end_date
         db.session.add(job)
         db.session.commit()
         return jsonify({"status":True,"id":f"job{id}","message":"<span class='text-success'>Woohoo! You have completed this job.</span>"})
      else:
         return jsonify({"status":False, "id":f"job{id}","message":"<span>Unable to mark as finished the job</span>"})


@sub_cont.route("/start/job/<id>")
@login_required
def start(id):
   if is_contractor(current_user.id):
      job = Status.query.filter_by(jobid = id, userid = current_user.id).first()
      if job and job.status == 1 or job.status == 3:
         date_time = datetime.now()
         start_date = date_time.strftime("%d-%m-%Y   %X")
         job.start_date = start_date
         db.session.add(job)
         db.session.commit()
         return jsonify({"status":True,"id":id,"message":"Finihed"})
      else:
         return jsonify({"status":False, "id":f"job{id}","message":"<span class='text-danger'>Unable to accept the job</span>"})
   else:
      logout_user()
      return redirect(url_for("admin.admin_login"))


@sub_cont.route("/profile/<userid>")
@login_required
def profile(userid):
   if is_contractor(current_user.id) and current_user.id == userid:
         try:
            page = request.args.get("page", 1, type = int) # will be used for ajax if time left
            contractor = current_user
            jobs = db.session.query(Status, Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).filter(Status.userid == contractor.id).all()
            details = contractor.details
            if jobs:
               accepted = Status.query.with_entities(Status.jobid).filter_by(user = contractor, status = 1).count()
               completed = Status.query.with_entities(Status.jobid).filter_by(user = contractor, status = 2).count()
               reassigned = Status.query.with_entities(Status.jobid).filter_by(user = contractor, status = 3).count()
               return render_template("/contractor/profile.html", title=f"Profile | {contractor.id}", details = details, jobs = jobs, accepted = accepted, completed = completed, reassigned = reassigned, userid = current_user.id)
            accepted = completed = reassigned = -1
            return render_template("/contractor/profile.html", title=f"Profile | {contractor.id}", details = details,  accepted = accepted, completed = completed, reassigned = reassigned, userid = current_user.id)
         except:
            flash("Sorry! Something went wrong.If this keeps on comming, kindly contact developer","danger")
            return redirect(url_for("admin.admin_view_contractor"))
   else:
      logout_user()
      return redirect(url_for("admin.admin_login"))

@sub_cont.route("/change_pass/<userid>", methods=['POST'])
@login_required
def change_pass(userid):
   if request.method == "POST":
      if is_contractor(current_user.id) and current_user.id == userid:
         if current_user.verify_password(request.form.get("old_pass")):
            password = request.form.get("pass","")
            new_pass = request.form.get("conf_pass","")
            if password == new_pass:
               current_user.set_password(password)
               db.session.add(current_user)
               db.session.commit()
               flash("Password updated successfully!","success")
            else:
               flash("New password and Confirm password should be same!","danger")
         else:
            flash("You entered wronge current password!","danger")
         return redirect(url_for("sub_cont.profile",userid = current_user.id))
      else:
         logout_user()
         flash("Please login!", "danger")
         return redirect(url_for("team_login"))
   else:
      abort(401)
