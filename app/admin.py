from operator import add
from flask import Blueprint, render_template, redirect, abort, request, session, url_for, flash, jsonify
from werkzeug.datastructures import ContentRange
from app.modal import AdminModal, Userlogin, Userdetail, Jobs, isdate, Status, is_admin, is_contractor
from flask_login import logout_user, current_user, login_user, login_required
from app import db
from datetime import datetime
import re
admin  =  Blueprint("admin", __name__, url_prefix="/admin")


# ----- admin zone started ------

# admin login route
@admin.route('/admin_login')
def admin_login():
    return render_template("/admin/admin_login.html")


@admin.route("/authenticate", methods=['POST'])
def admin_auth():
    if request.method == "POST":
        admin = AdminModal.query.get(request.form.get("adminid"))
        if admin is not None and admin.verify_password(request.form.get("adminpass")):
            login_user(admin)
            return redirect(url_for("admin.admin_index"))
        else:
            flash("Login is required!", "danger")
            return redirect(url_for("admin.admin_login"))
    else:
        abort(405)


#admin home page (Login Required)
@admin.route('/home')
@login_required
def admin_index():
    if is_admin(current_user.id):
        return render_template("/admin/admin_home.html", title="Admin Home")
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))


@admin.route("/add/jobs")
@login_required
def add_jobs():
    if is_admin(current_user.id):
        return render_template("/admin/add_jobs.html", title="Add Jobs")
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))

@admin.route("/add/jobs", methods=['POST'])
@login_required
def post_jobs():
    if is_admin(current_user.id):   
        try:
            if request.method == "POST":
                country_code = "+61"
                country_number_len = {"+91":10, "+61":9}
                number = request.form.get("number", "")
                computed_number = country_code + " " +number[:country_number_len.get(country_code, 10)]
                job = Jobs(
                        job_title = request.form.get("title", ""),
                        client_name = request.form.get("client", ""),
                        workdate = request.form.get("work_date", ""),
                        contact_no = computed_number,
                        job_detail = request.form.get("details", ""),
                        address = request.form.get("address", ""),
                        client_note = request.form.get("note")
                    )
                if job.job_title != '' and job.client_name != "" and job.workdate != "" and isdate(job.workdate) and job.contact_no != "" and len(number) == country_number_len.get(country_code) and job.job_detail != "" and job.address != "":
                    id = job.copy_to_status_table()
                    db.session.add(job)
                    db.session.commit()
                    message = f"""
                    <div class='head-2'>
                        Job added succesfully.
                    </div>
                    <div>
                        Job Id - {id}<br/>
                        Title - {job.job_title}
                    </div>
                    """
                    flash(message, "success")
                else:  
                    flash("Please enter all the required feilds.","danger")
            return redirect(url_for("admin.add_jobs"))
        except:
            flash(f"Error Occurred","danger")
            return redirect(url_for("admin.add_jobs"))
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))


@admin.route("/add/contractor")
@login_required
def add_contractor():
    if is_admin(current_user.id):
        return render_template("/admin/add_contractor.html", title="Add Contractor")
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))

@admin.route("/add/contractor", methods=['POST'])
@login_required
def post_contractor():
    if is_admin(current_user.id):
        try:
            if request.method == "POST":
                business_contact_name =  request.form.get("business_contact_name","")
                abn = request.form.get("abn","")[:11]
                country_code = "+61" #hardcoded country code
                number = request.form.get("contact_no","")
                email = request.form.get("email","")
                address = request.form.get("address","")
                country_number_len = {"+91": 10, "+61": 9} #country_code dict
                number_len = country_number_len.get(country_code, None) #getting country contact number length
                if business_contact_name != "" and abn != "" and len(abn) == 11 and number_len is not None and number != "" and email != "" and address != "":
                    # checking email
                    regex = r'[a-z0-9A-Z]+(\.+[a-z0-9A-Z]+)*@+[a-z]+(\.+[a-z]+)+' #regex
                    email_check = re.match(regex, email)
                    if email_check:
                        if len(number) == number_len:
                            number = country_code + " " + number[:number_len]
                            primary_check = Userdetail.query.filter((Userdetail.email == email) | (Userdetail.abn == int(abn)) | (Userdetail.mob_number == number)).first()
                            if not primary_check:
                                contractor = Userdetail(email = email, abn = abn, mob_number = number, business_contact_name = business_contact_name, address = address)
                                login, password = contractor.create_login()
                                db.session.add(contractor)
                                db.session.add(login)
                                db.session.commit()
                                message = f"""
                                <h5>Sub-Contractor registered successfully!</h5>
                                <div class="head-2 pt-3">Business/Contact Name</div>
                                <div>{contractor.business_contact_name}</div>
                                <div class="head-2 pt-3">User Id</div>
                                <div>{login.id}</div>
                                <div class="head-2 pt-3">Password</div>
                                <div>{password}</div>
                                <div class="pt-4"><span class="head-2">Note:</span> Please take note of these login credentials before reloading this page, so that it can me given to the Sub-Contractor. Without this Sub-Contractor will not be able to login.</div>
                                """
                                flash(message,"success")
                            else:
                                if primary_check.email == email:
                                    flash("A Sub-Contractor is already registered with this email!","danger")
                                elif primary_check.abn == int(abn):
                                    flash("A Sub-contractor is already registered with this ABN Number!", "danger")
                                elif primary_check.mob_number == number:
                                    flash("A Sub-Contractor is already registered with this Mobile Number!", "danger")
                        else:
                            flash(f"Invalid Contact number. Contact number should be of {number_len} digits but {len(number)} digits found","danger")
                    else:
                        flash("Invalid Email!", "danger")
                else:
                    flash("All feilds are required. Please fill all the feilds.","danger")

            return redirect(url_for("admin.add_contractor"))
        except Exception as e:
            flash(f"Error Occurred!{e}", "danger")
            return redirect(url_for("admin.add_contractor"))
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))

# route to view all the jobs by admin (Login Required)
"""
in this route we are directly delivering the data of any filtered data or empty filter data
but
if user wants to get it by ajax then we have another route /admin/request/jobs/<fiterid>
"""
@admin.route("/view/jobs/")
@admin.route("/view/jobs/<filter>")
@login_required
def admin_view_jobs(filter = "1"):
    if is_admin(current_user.id):
        try:
            title_dict = {
                "1": "All Jobs", "2":"Jobs Posted Today","3": "Active Jobs", "4":"Completed Jobs", "5":"Reassigned Jobs", "6":"To-do Today"
            }
            if filter == "1":
                jobs = Jobs.query.order_by(Jobs.id.desc()).all()
                if not jobs:
                    flash("No jobs posted!<a href='/admin/add/jobs'>Post Jobs</a>","info")
            elif filter == "2":
                date_time = datetime.now()
                date = date_time.strftime("%d-%m-%Y")
                jobs = Jobs.query.filter_by(post_date = date).order_by(Jobs.id.desc()).all()
                if not jobs:
                    flash("No new jobs!","info")
            elif filter == "3":
                jobs = Status.query.filter_by(status = 1).order_by(Status.jobid.desc()).all()
                if not jobs:
                    flash("No jobs with status as Accepted!","info")
            elif filter == "4":
                jobs = Status.query.filter_by(status = 2).order_by(Status.jobid.desc()).all()
                if not jobs:
                    flash("No jobs with status as Completed!","info")
            elif filter == "5":
                jobs = Status.query.filter_by(status = 3).order_by(Status.jobid.desc()).all()
                if not jobs:
                    flash("No jobs with status as Reassigned!","info")
            elif filter == "6":
                date_time = datetime.now()
                date = date_time.strftime("%Y-%m-%d")
                jobs = Jobs.query.filter_by(workdate = date).order_by(Jobs.post_date.desc(), Jobs.post_time.desc()).all()
                if not jobs:
                    flash("No jobs to-do today!","info")
            else:
                flash("Invalid filter! So all jobs are been displayed to you.","warning")
                return redirect(url_for("admin.admin_view_jobs"))
            return render_template("/admin/view_jobs.html", title=title_dict.get(filter), value = filter, jobs = jobs)
        except Exception as e:
            flash(f"Sorry! Something went wrong.If this keeps on comming, kindly contact developer.{e}","danger")
            return render_template("/admin/view_jobs.html", title=title_dict.get(filter), value = filter)
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))


@admin.route("/view/contractor/")
@admin.route("/view/contractor/<filter>")
@login_required
def admin_view_contractor(filter = "-1"):
    if is_admin(current_user.id):
        try:
            if filter == "1":
                contractors = Userdetail.query.all()
            elif filter == "-1":
                contractors = Userdetail.query.order_by(Userdetail.row_count.desc()).all()
            else:
                flash("Invalid filter! So filter is default filter.","warning")
                return redirect(url_for("admin.admin_view_contractor"))
            if not contractors:
                flash("No contractor added yet.<a href = '/admin/add/contractor'>Add Contractors</a>","info")
            return render_template("/admin/view_contractor.html", title="Contactor's List", value = filter, contractors = contractors)
            
        except:
            flash("Sorry! Something went wrong.If this keeps on comming, kindly contact developer","danger")
            return render_template("/admin/view_contractor.html", title="Contactor's List", value = filter)
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))


@admin.route("/open/contractor/<userid>")
@login_required
def open_contractor(userid = None):
    if is_admin(current_user.id):
        # try:
            page = request.args.get("page", 1, type = int) # will be used for ajax if time left
            contractor = Userlogin.query.filter_by(id = userid).first_or_404()
            if contractor.is_active == 1:
                acc_status = "Active"
                next_type = 'Deactivate'
            else:
                acc_status = "Deactivated"
                next_type = 'Activate'
            jobs = db.session.query(Status, Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).filter(Status.userid == contractor.id).all()
            details = contractor.details
            if jobs:
                accepted = Status.query.with_entities(Status.jobid).filter_by(user = contractor, status = 1).count()
                completed = Status.query.with_entities(Status.jobid).filter_by(user = contractor, status = 2).count()
                reassigned = Status.query.with_entities(Status.jobid).filter_by(user = contractor, status = 3).count()
                return render_template("/admin/profile.html", title=f"Profile | {contractor.id}", details = details, jobs = jobs, accepted = accepted, completed = completed, reassigned = reassigned, acc_status = acc_status, next_type = next_type)
            accepted = completed = reassigned = -1
            return render_template("/admin/profile.html", title=f"Profile | {contractor.id}", details = details,  accepted = accepted, completed = completed, reassigned = reassigned, acc_status = acc_status, next_type = next_type)
        # except Exception as e:
        #     flash(f"Sorry! Something went wrong.If this keeps on comming, kindly contact developer{e}","danger")
        #     return redirect(url_for("admin.admin_view_contractor"))
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))


@admin.route("/open/job/<id>")
@login_required
def admin_open_jobs(id):
    """This function return the job details to the admin along with user who accepted the job if anyone has accepted"""
    try:
        if is_admin(current_user.id):
            jobs = db.session.query(Status,Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).order_by(Status.jobid.desc()).filter(Status.jobid == int(id)).first()
            if jobs: 
                job = jobs[0]
                detail = jobs[1]
                user = job.user
                print(job.status)
                print(type(job.end_date),job.end_date)
                if user:
                    user = user.details
                else:
                    user = None
                status = job.status
                dict = {
                    "0":"Pending",
                    "1":"Accepted",
                    "2":"Completed",
                    "3":"Reassigned",
                }
                current_status = dict.get(str(status))
                html = render_template("/admin/view_jobs_modal_template.html", job = jobs, detail = detail, user = user, status = status, current_status = current_status, end_date = job.end_date, start_date = job.start_date)
                return jsonify({"status":True, "html":html})
            else:
                return jsonify({"status":False, "message":"Invalid userid!"})
        else:
            logout_user()
            flash("Login is required!")
            return redirect(url_for("admin.admin_login"))
    except Exception as e:
        message = f"Sorry! Something went wrong.If this keeps on comming, kindly contact developer: {e}"
        return jsonify({"status":False,"message":message})

@admin.route("/delete/job/<id>")
@login_required
def admin_delete_jobs(id):
    """ this will delete the jobs based on id transfered by the admin. """
    if is_admin(current_user.id):
        try:
            job = Status.query.filter_by(jobid = int(id)).first()
            if job:
                db.session.delete(job)
                db.session.commit()
                flash("Job deleted successfully.","success")
            else:
                flash("No such jobs present, so cannot be deleted", "danger")
            return redirect(url_for("admin.admin_view_jobs"))
        except:
            flash("Sorry! Something went wrong.If this keeps on comming, kindly contact developer","danger")
            return redirect(url_for("admin.admin_view_jobs"))
    else:
        logout_user()
        flash("Login is required!")
        return redirect(url_for("admin.admin_login"))


@admin.route("/shuffle/contractor/<userid>/<acc_type>")
@login_required
def shuffle_acc_type(userid, acc_type):
    """ this will active or deactive user the jobs based on useid transfered by the admin. """
    if is_admin(current_user.id):
        try:
            user = Userlogin.query.filter_by(id = userid).first()
            if user:
                dict = {
                    "Activate":1,
                    "Deactivate": 2
                }
                user.is_active = dict.get(acc_type, 1)
                db.session.add(user)
                db.session.commit()
                flash(f"Contractor {acc_type}d successfully.","success")
            else:
                flash("No such contractor present", "danger")
            return redirect(f"/admin/open/contractor/{userid}")
        except:
            flash("Sorry! Something went wrong.If this keeps on comming, kindly contact developer","danger")
            return redirect(f"/admin/open/contractor/{userid}")
    else:
        logout_user()
        flash("Login is required!")
        return redirect(url_for("admin.admin_login"))


@admin.route("/edit_contractor/<userid>")
@login_required
def edit_contractor(userid):
    if is_admin(current_user.id):
        user = Userdetail.query.filter_by(userid = userid).first()
        if user:
            return render_template("/admin/edit_contractor.html", title="Add Contractor", user = user)
        else:
            flash("Unable to edit.","danger")
            return redirect(url_for("admin.admin_view_contractor"))
    else:
        logout_user()
        return redirect(url_for("admin.admin_login"))

@admin.route("/change_contractor/<userid>", methods=['POST'])
@login_required
def change_contractor(userid):
    try:
        if is_admin(current_user.id):
            user = Userdetail.query.filter_by(userid = userid).first()
            if user:
                if request.method == "POST":
                    business_contact_name =  request.form.get("business_contact_name","")
                    abn = request.form.get("abn","")[:11]
                    country_code = "+61" #hardcoded country code
                    email = request.form.get("email","")
                    address = request.form.get("address","")
                    if business_contact_name != "" and abn != "" and len(abn) == 11 and email != "" and address != "":
                        # checking email
                        regex = r'[a-z0-9]+(\.+[a-z0-9]+)*@+[a-z]+(\.+[a-z]+)+' #regex
                        email_check = re.match(regex, email)
                        if email_check:
                                user.email = email
                                user.abn = abn
                                user.business_contact_name = business_contact_name
                                user.address = address
                                db.session.add(user)
                                db.session.commit()
                                flash("Edited successfully","success")
                        else:
                            flash("Email is in use.","warning")
                return redirect(url_for("admin.admin_view_contractor"))
            else:
                flash("Unable to edit.","danger")
                return redirect(url_for("admin.admin_view_contractor"))
        else:
            logout_user()
            return redirect(url_for("admin.admin_login"))
    except:
        flash("Sorry! Something went wrong.If this keeps on comming, kindly contact developer","danger")
        return redirect(url_for("admin.admin_view_contractor"))

#----- admin zone ended ----------