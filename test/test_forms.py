import unittest
import forms
import models
from flask import Flask, request, jsonify


class Test_Forms(unittest.TestCase):
    
    def request(self,*args, **kwargs):
        return self.app.test_request_context(*args, **kwargs)
    
    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        
        models.User.create_user(
            username="test_form_user",
            email="test_form_user@example.com",
            password="test_models_user_pw"
            )
        self.user = models.User.get(models.User.username == "test_form_user")
   
    def tearDown(self):
        self.ctx.pop()
        self.user.delete_instance()
        self.user = None
        
    def create_app(self):
        app = Flask(__name__)
        app.secret_key = 'secret'


        return app
        
class Test_Register_Form(Test_Forms):
    def test_register_valid_data(self):
        with self.request(method='POST', data={'username':'test_form_reg', 
                    'email':'test_form@example.com',
                    'password':'test_password',
                    'password2':'test_password'}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), True)
            
    def test_register_invalid_email_no_domain(self):
        with self.request(method='POST',data={'username':'test_form_reg', 
                    'email':'test_form_user',
                    'password':'test_password',
                    'password2':'test_password'}):
            form = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(form.validate_on_submit(), False)
    
    def test_register_invalid_email_incorrect_domain(self):
        with self.request(method='POST',data={'username':'test_form_reg', 
                    'email':'test_form_user@test',
                    'password':'test_password',
                    'password2':'test_password'}):
            form = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(form.validate_on_submit(), False)
            
    def test_register_invalid_username_special_character(self):
        with self.request(method='POST',data={'username':'test_user?', 
                    'email':'test_form_user@test.com',
                    'password':'test_password',
                    'password2':'test_password'}):
            form = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(form.validate_on_submit(), False)
            
    def test_register_different_passwords(self):
        with self.request(method='POST',data={'username':'test_user', 
                    'email':'test_form_user@test.com',
                    'password':'test_password',
                    'password2':'password'}):
            form = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(form.validate_on_submit(), False)
            
    def test_register_password_too_short(self):
        with self.request(method='POST',data={'username':'test_user', 
                    'email':'test_form_user@test.com',
                    'password':'p',
                    'password2':'pa'}):
            form = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(form.validate_on_submit(), False)
            
    def test_register_no_username(self):
        with self.request(method='POST', data={'username':'', 
                    'email':'test_form_user@example.com',
                    'password':'test_password',
                    'password2':'test_password'}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_register_no_email(self):
        with self.request(method='POST', data={'username':'test_form_reg', 
                    'email':'',
                    'password':'test_password',
                    'password2':'test_password'}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_register_no_password(self):
        with self.request(method='POST', data={'username':'test_form_reg', 
                    'email':'test_form_user@example.com',
                    'password':'',
                    'password2':'test_password'}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_register_no_password2(self):
        with self.request(method='POST', data={'username':'test_form_reg', 
                    'email':'test_form_user@example.com',
                    'password':'test_password',
                    'password2':''}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_register_duplicate_username(self):
        with self.request(method='POST', data={'username':'test_form_user', 
                    'email':'test_form_@example.com',
                    'password':'test_password',
                    'password2':'test_password'}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_register_duplicate_email(self):
        with self.request(method='POST', data={'username':'test_form_reg', 
                    'email':'test_form_user@example.com',
                    'password':'test_password',
                    'password2':'test_password'}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_register_no_data(self):
        with self.request(method='POST', data={}):
            f = forms.RegisterForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
class Test_Login_Form(Test_Forms):
    def test_login_no_data(self):
        with self.request(method='POST', data={}):
            f = forms.LoginForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_login_vaild_data(self):
        with self.request(method='POST', data={'email':'test_login@example.com',
                    'password':'test'}):
            f = forms.LoginForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), True)
    
    def test_login_invalid_email(self):
        with self.request(method='POST', data={'email':'test_user',
                    'password':'test'}):
            f = forms.LoginForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_login_no_email(self):
        with self.request(method='POST', data={'email':'',
                    'password':'test'}):
            f = forms.LoginForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_login_no_password(self):
        with self.request(method='POST', data={'email':'test_user',
                    'password':''}):
            f = forms.LoginForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
class Test_Post_Form(Test_Forms):
    def test_post_no_data(self):
        with self.request(method='POST', data={}):
            f = forms.PostForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), False)
            
    def test_post_valid_data(self):
        with self.request(method='POST', data={'content':'new post'}):
            f = forms.PostForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), True)
            
if __name__ == '__main__':
    unittest.main()
                