from sqlalchemy import func, or_
from app import db, login_manager
from flask_login import UserMixin
from passlib.hash import sha256_crypt as crypt
from app import param
from flask import flash
import random
import array
import re
from datetime import datetime, timedelta


@login_manager.user_loader
def load_user(id): 
    if is_admin(id):
        return AdminModal.query.get(id)
    else:
        user = Userlogin.query.filter(Userlogin.id == id).first()
        if user.is_active != 1:
            flash("Your account has been deactivated","info")
            return None
        else:
            return user

def isdate(date):
    try:
        if date is None or date == "":
            return False
        else:
            regex = [r"\d{4}-\d{2}-\d{2}", r"\d{2}-\d{2}-\d{4}"]
            for ex in regex:
                match = re.match(ex, date)
                if match:
                    return True
            return False
    except:
        return False

def is_admin(adminid):
    try:
        split_list = adminid.split(".")
        id, code = split_list[:2]
        return len(split_list) == 2 and id.startswith("$") and code == "admin"
    except:
        return False


def is_contractor(s):
    try:
        regex = r"knl\d+"
        contractor = str(s)
        parts = contractor.split(".")
        match = re.match(regex, parts[1])
        sufix = match.group()
        return len(parts) == 2 and parts[0].isalnum() and parts[1] == sufix 
    except:
        return False

def get_upcomming_seven_day_jobs(user):
    try:
        dates = []
        for i in range(7):
            dates.append((datetime.now() + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        jobs = db.session.query(Status, Jobs).outerjoin(Jobs, Status.jobid == Jobs.id).\
            filter(or_(Jobs.workdate == dates[0], Jobs.workdate == dates[1], Jobs.workdate == dates[2], Jobs.workdate == dates[3], Jobs.workdate == dates[4], Jobs.workdate == dates[5], Jobs.workdate == dates[6]), Status.userid == user)\
            .order_by(Jobs.post_date.desc(), Jobs.post_time.desc())
        return jobs
    except:
        return None


class AdminModal(UserMixin, db.Model):
    __tablename__  = "contractor"
    index = db.Column(db.Integer, unique = True)
    id = db.Column(db.String, primary_key = True) # it should be present as it is used by the Flask-Login

    def is_active(self):
        print("Hello")
        return self.index

    def setindex(self):
        self.index = AdminModal.query.count()

    def strip(self, str):
        return str.strip()

    def get_password(self, index):
        try:
            return list(map(self.strip,param.get("admin-password").split(",")))[index]
        except:
            return ""

    def verify_password(self, password):
        return crypt.verify(password, self.get_password(self.index))


class Userlogin(UserMixin,db.Model):
    """
    Warning: deleting Contractor will also delete the Jobs from status table which are accepts ever by the contractor
    """
    __tablename__ = "userlogin"

    id = db.Column(db.String(80), primary_key = True)
    password = db.Column(db.String, nullable = False)
    is_active = db.Column(db.Integer, nullable = False, default = 1)
    details = db.relationship("Userdetail", backref = "userlogin", cascade = "all, delete-orphan", uselist = False)
    jobs = db.relationship("Status", backref = "user", cascade = "all, delete-orphan")

    def generate_random_password(self):
        MAX_LEN = 12
        DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']  
        LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 
                            'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                            'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                            'z']
 
        UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
                            'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                            'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                            'Z']
 
        SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>', 
                    '*', '(', ')', '<']
        COMBINED_LIST = DIGITS + LOCASE_CHARACTERS + UPCASE_CHARACTERS + SYMBOLS
        random_digit = random.choice(DIGITS)
        random_locase = random.choice(LOCASE_CHARACTERS)
        random_upcase = random.choice(UPCASE_CHARACTERS)
        random_symbol = random.choice(SYMBOLS)

        temp_pass = random_digit + random_locase + random_upcase + random_symbol

        for _ in range(MAX_LEN - 4):
            temp_pass += random.choice(COMBINED_LIST)
        temp_pass_list = array.array("u", temp_pass)
        random.shuffle(temp_pass_list)
        
        # fetching password
        password = ""
        for char in temp_pass_list:
            password += char
        return password
        
    def set_password(self, password):
        self.password = crypt.hash(password)

    def verify_password(self, password):
        return crypt.verify(password, self.password)

class Userdetail(db.Model):
    __tablename__ = "userdetail"

    row_count = db.Column(db.Integer, primary_key = True, autoincrement = True)
    email = db.Column(db.String(100), unique = True, nullable = False)
    abn = db.Column(db.Integer,unique = True, nullable = False)
    mob_number = db.Column(db.String(15), unique = True, nullable = False)
    business_contact_name = db.Column(db.String(200), nullable = False)
    address = db.Column(db.Text,nullable = False)
    userid = db.Column(db.String(80), db.ForeignKey("userlogin.id", ondelete = "CASCADE"), unique = True, nullable = False)
    date = db.Column(db.String(35), nullable = False)
    time = db.Column(db.String(15), nullable = False)

    def create_login(self):
        login = Userlogin()
        if not Userdetail.query.first():
            index = 0
        else:
            index = Userdetail.query.with_entities(func.max(Userdetail.row_count)).first()[0]
        userid = self.email.split("@")[0] + f".knl{index}"
        login.id = userid
        password = login.generate_random_password()
        login.set_password(password)

        # adding generated userid and generation time to the userdetail of the sub-contractor
        self.userid = userid
        date_time = datetime.now()
        generation_date = date_time.strftime("%d-%m-%Y")
        generation_time = date_time.strftime("%X")
        self.date = generation_date
        self.time = generation_time
        return login, password


class Jobs(db.Model):
    __tablename__ = "jobs"
    
    id = db.Column(db.Integer, db.ForeignKey("status.jobid", ondelete = "CASCADE"), primary_key = True, nullable = False)
    job_title = db.Column(db.String(200), nullable = False)
    job_detail = db.Column(db.Text, nullable = False)
    client_name = db.Column(db.String(200), nullable  = False)
    contact_no = db.Column(db.String(15), nullable = False)
    address = db.Column(db.Text, nullable = False)
    client_note = db.Column(db.Text, default = " ")
    workdate = db.Column(db.String(20), nullable = False)
    post_date = db.Column(db.String(35), nullable = False)
    post_time = db.Column(db.String(15), nullable = False)

    def copy_to_status_table(self):
        status_obj = Status()
        if not Status.query.first():
            self.id = 1
        else:
            self.id = Status.query.with_entities(func.max(Status.jobid)).first()[0]+1
        if not self.post_date:
            date_time = datetime.now()
            generation_date = date_time.strftime("%d-%m-%Y")
            generation_time = date_time.strftime("%X")
            self.post_date = generation_date
            self.post_time = generation_time
        db.session.add(status_obj)
        return self.id

class Status(db.Model):
    __tablename__ = "status"

    jobid = db.Column(db.Integer, primary_key = True, autoincrement = True)
    userid = db.Column(db.String(80),db.ForeignKey("userlogin.id", ondelete = "CASCADE"))
    status = db.Column(db.Integer, nullable = False, default = 0)
    detail = db.relationship("Jobs", backref = "status", cascade = "all, delete-orphan", lazy = "select", uselist = False)
    # 1 = accepted, 2 = Completed, 3 = Reassigned
    start_date = db.Column(db.String(35))
    end_date = db.Column(db.String(35))
