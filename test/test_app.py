#Accountable Politics
#test_app.py


import unittest
import tempfile
import requests
from app import *



class Test_App(unittest.TestCase):
    
    #render_templates = False
    
    @classmethod
    def setUpClass(self):
        print("Initializing Test Instances...")

        # create a tempfile db
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # self.form = forms.RegisterForm()    
        # self.form.username.data = "test_user"
        # self.form.email.data = "test_user@example.com"
        # self.form.password.data = "test_password"
        # self.form.password2.data = "test_password"

    @classmethod
    def tearDownClass(self):
        print("Deleting Test Instances")
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
   
    def test_register(self):
        payload = {'username':'test_user_reg', 
                    'email':"test_user@example.com",
                    "password":"test_password",
                    "password2":"test_password"}
        #session = requests.Session()                
        #session.post('/register', params = payload)
        try:
            result = self.app.post('/register', data = payload, follow_redirects=True)
            self.user = models.User.get(models.User.username == "test_user_reg")
        except:
            self.assertTrue(0)
        else:
            self.assertTrue(1)
        
        
    def test_register_duplicate_email(self):
        payload = {'username':'test_user_reg5', 
                    'email':"test_user@example.com",
                    "password":"test_password",
                    "password2":"test_password"}
        try:
            result = self.app.post('/register', data = payload, follow_redirects=True)
            user = models.User.get(models.User.username == "test_user_reg5")
        except:
            self.assertTrue(1)
        else:
            self.assertTrue(0)
            
    def test_register_duplicate_username(self):
        payload = {'username':'test_user_reg', 
                    'email':"test_user1@example.com",
                    "password":"test_password",
                    "password2":"test_password"}
        try:
            result = self.app.post('/register', data = payload, follow_redirects=True)
            user = models.User.get(models.User.username == "test_user_reg5")
        except:
            self.assertTrue(1)
        else:
            self.assertTrue(0)
            
    def test_login(self):
        with self.app:
            payload = {'email':"test_user@example.com",
                        'password':"test_password"}
            self.app.post('/login', data = "", follow_redirects=True)
            f = self.LoginForm()
            f.email = "test_user@example.com"
            f.password = "test_password"
            
            print(f.validate_on_submit())
            #self.assertEqual(f.is_submitted(), False)
            
        
    # def register_form(self, Form, username, email, password):
    #     self.form.username = username
    #     self.form.email = email
    #     self.form.password, self.form.password2 = password
        
    # def login(self, username, password):
    #     return self.app.post('/login', data = dict(
    #         username = username,
    #         password = password),
    #         follow_redirect = True)
    
    # def logout(self):
    #     return self.app.get('/logout', follow_redirect = True)
    
    # def test_register(self):
    #     self.register()
    #     self.assertIsNotNone(models.User.get(models.User.username == "test_user_reg"))
        # print(rv.data.decode("UTF-8"))
        # assert "You successfully signed up!" in rv.data.decode("UTF-8")
        
    # def test_login_logout(self):
    #     rv = self.login("test_models_user", "test_models_user_pw")
    #     assert "You are logged in!" in rv.data
        
if __name__ == '__main__':
   unittest.main()