from flask import Blueprint, render_template, redirect, url_for, abort, request, jsonify, flash
from flask_login import login_required, current_user, logout_user, login_user
from app.modal import Userlogin, is_admin, is_contractor, Status, db, Jobs, datetime

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
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.status == 1).all()
            return render_template("/contractor/filter_jobs.html",title="Active Jobs", filter = filter, inprogress = True, jobs = jobs, userid = current_user.id)

         elif filter == "3":
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.status == 2).all()
            return render_template("/contractor/filter_jobs.html",title="Completed Jobs", filter = filter, jobs = jobs, userid = current_user.id)

         elif filter == "4":
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.status == 3).all()
            return render_template("/contractor/filter_jobs.html",title="Reassigned Jobs", filter = filter, jobs = jobs, userid = current_user.id)
      except Exception as e:
         flash(f"Error Occurred: {e}", "danger")
         return render_template("/contractor/filter_jobs.html",title="View Jobs", filter = filter, userid = current_user.id)


@sub_cont.route("/accept/job/<id>")
@login_required
def accept(id):
   if is_contractor(current_user.id):
      job = Status.query.filter_by(jobid = id, status = 0).first()
      if job:
         job.status = 1
         job.userid = current_user.id
         date_time = datetime.now()
         start_date = date_time.strftime("%d-%m-%Y")
         job.start_date = start_date
         db.session.add(job)
         db.session.commit()
         return jsonify({"status":True,"message":"Accepted <i class='fa fa-check'></i>"})
      else:
         return jsonify({"status":False, "id":f"job{id}","message":"<span class='text-danger'>Unable to accept the job</span>"})

@sub_cont.route("/finished/job/<id>")
@login_required
def finish(id):
   if is_contractor(current_user.id):
      job = Status.query.filter_by(jobid = id, userid = current_user.id).first()
      if job and job.status == 1 or job.status == 3:
         job.status = 2
         date_time = datetime.now()
         end_date = date_time.strftime("%d-%m-%Y")
         job.end_date = end_date
         db.session.add(job)
         db.session.commit()
         return jsonify({"status":True,"id":f"job{id}","message":"<span class='text-success'>Woohoo! You have completed this job.</span>"})
      else:
         return jsonify({"status":False, "id":f"job{id}","message":"<span>Unable to mark as finished the job</span>"})

@sub_cont.route("/profile/<userid>")
@login_required
def profile(userid):
   pass