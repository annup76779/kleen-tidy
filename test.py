from app import app, db, modal
import unittest


class FlaskTestCase(unittest.TestCase):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///modal.db"
    db.create_all()
    if not modal.AdminModal.query.first():
        admin = modal.AdminModal(id = "$annup76779.admin")
        admin.setindex()
        db.session.add(admin)
        db.session.commit()
    
    password = ""
    userid = ""
    if not modal.Userlogin.query.first():
        user = modal.Userdetail(
            business_contact_name = "lakdfjlkadj",
            email = "annup76779@gmail.com",
            abn = 12345678901,
            mob_number = "+61 123456789",
            address = "Australia"
        )
        login, password = user.create_login()
        userid = login.id
        db.session.add(login)
        db.session.add(user)
        db.session.commit()
    else:
        user = modal.Userlogin.query.first()
        password = user.generate_random_password()
        user.set_password(password)
        userid = user.id
        db.session.add(user)
        db.session.commit()

    # # admin login behaves correctly with correct data
    def test_4_admin_login_login_correct_data(self):
        tester = app.test_client(self)
        data = dict(adminid = "$annup76779.admin", adminpass = "76779")
        response = tester.post("/admin/authenticate", data = data, follow_redirects = True)
        self.assertTrue(b"Contractor Details" in response.data)


    # # admin login behaves correctly with incorrect data
    def test_5_admin_login_login_incorrect_data(self):
        tester = app.test_client(self)
        data = dict(adminid = "$addhdf8738.admin", adminpass = "If?fZGW8dksfjksy2f#")
        response = tester.post("/admin/authenticate", data = data, follow_redirects = True)
        self.assertTrue(b"Admin Login" in response.data)
        
    # # Admin login behaves correctly with  data
    def test_6_admin_logout(self):
        tester = app.test_client(self)
        data = dict(adminid = "$annup76779.admin", adminpass = "76779")
        tester.post("/admin/authenticate", data = data, follow_redirects = True)     
        response = tester.get("/logout",follow_redirects = True)
        self.assertTrue(b"Admin Login" in response.data)

    # adding new user to the Database
    def test_7_admin_add_sub_contractor(self):
        tester = app.test_client(self)
        data = dict(adminid = "$annup76779.admin", adminpass = "76779")
        tester.post("/admin/authenticate", data = data, follow_redirects = True)    
        data = dict(
            business_contact_name = "DhanyaVittaldass",
            abn = 49832443234,
            contact_no = 678543234,
            email = "dhanyavittaldas@gmail.com",
            address = "Kerela"
        )
        response = tester.post("/admin/add/contractor",data = data, follow_redirects = True)
        self.assertTrue(b"Add Sub-Contractor" in response.data)

    def test_8_admin_add_new_job(self):
        tester = app.test_client(self)
        data = dict(adminid = "$annup76779.admin", adminpass = "76779")
        tester.post("/admin/authenticate", data = data, follow_redirects = True)    
        data = dict(
            title = "glass clean",
            client = "Dhanya",
            work_date = "2020-12-2",
            number = 789906543,
            details = "hsjfhjsdk",
            address = "Kerela",
            note = "sfsdjkfhsjhfjhsd"
        )
        response = tester.post("/admin/add/jobs",data = data, follow_redirects = True)
        self.assertTrue(b"Add Jobs" in response.data)

    # opens up the team logon Route
    def test_1_team_login_status(self):
        tester = app.test_client(self)
        response = tester.get("/", content_type = "html/text")
        self.assertEqual(response.status_code, 200)
   
    # testing the correct login page is rendered to the user i.e. /general/team_login.html
    def test_2_team_login_loads(self):
        tester = app.test_client(self)
        response = tester.get("/",content_type = "html/text")
        self.assertTrue(b"Sub-Contractor Login" in response.data)
    
    # login behaves correctly with correct data
    def test_3_team_login_login_correct_data(self):
        tester = app.test_client(self)
        data = dict(userid = FlaskTestCase.userid, password = FlaskTestCase.password)
        response = tester.post("/contractor/authentication", data = data, follow_redirects = True)
        self.assertTrue(b"Welcome to the contractor Protal" in response.data)
    # login behaves correctly with incorrect data
    def test_4_team_login_login_incorrect_data(self):
        tester = app.test_client(self)
        data = dict(userid = "dhanyavittaldas.knl1", password = "If?fZGW8dksfjksy2f#")
        response = tester.post("/contractor/authentication", data = data, follow_redirects = True)
        self.assertTrue(b"Sub-Contractor Login" in response.data)
        
    # # login behaves correctly with  data
    def test_3_team_logout_sub_contractor(self):
        tester = app.test_client(self)
        data = dict(userid = FlaskTestCase.userid, password = FlaskTestCase.password)
        tester.post("/contractor/authentication", data = data, follow_redirects = True)     
        response = tester.get("/logout",follow_redirects = True)
        self.assertTrue(b"Sub-Contractor Login" in response.data)

    # ensures cotractor home page requires login
    def test_4_home_page_requires_login(self):
        tester = app.test_client(self)
        response = tester.get("/contractor/home", content_type = "html/text", follow_redirects = True)
        self.assertTrue(b"Login is required!" in response.data)

if __name__ == "__main__":
    unittest.main()