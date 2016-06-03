#Accountable Politics
#test_models.py

import unittest
import models

from flask.ext.bcrypt import check_password_hash
import datetime
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo)

class Test_Models(unittest.TestCase):
 
#   TEST CASE SET UP    #

    @classmethod
    def setUpClass(self):
        print("Initializing Test Instances...")
        
        print("> Creating Users: ", end='')
        #create a test user
        models.User.create_user(
            username="test_models_user",
            email="test_models_user@example.com",
            password="test_models_user_pw"
            )
        self.user = models.User.get(models.User.username == "test_models_user")
        
        print("User1 created", end='')
        
        #create a 2nd test user
        models.User.create_user(
            username="test_models_user2",
            email="test_models_user2@example.com",
            password="test_models_user2_pw"
            )
        self.user2 = models.User.get(models.User.username == "test_models_user2")

        print(", User2 created")
        
        print("> Creating Posts: ", end='')
        #create a test post for user
        models.Post.create(user = self.user, content = "test post content")
        self.post = models.Post.get(models.Post.user == self.user)
        print("post1 created", end='')
        
        #create a test post for user2
        models.Post.create(user = self.user2, content = "test post content 2")
        self.post2 = models.Post.get(models.Post.user == self.user2)
        print(", post2 created")
        
        print("> Creating Relationship: ", end='')
        
        #create Relationship: user follows user2
        models.Relationship.create(from_user = self.user, to_user = self.user2)
        self.relationship = models.Relationship().get(
                                    models.Relationship.from_user == self.user)
        print("User1 following User2")
        
#   TEST CASE TEAR DOWN     #
    @classmethod
    def tearDownClass(self):
        print("Deleting Test Instances")
        self.user.delete_instance()
        self.user = None
        self.user2.delete_instance()
        self.user2 = None
        self.post.delete_instance()
        self.post = None
        self.post2.delete_instance()
        self.post2 = None
        self.relationship.delete_instance()
        self.relationship = None

#   USER TABLE TESTS  #

    def test_user_created(self):
        self.assertIsNotNone(self.user, "user was not created")

    def test_user_attribute_username(self):
        self.assertEqual(self.user.username, "test_models_user", 
                                            "incorrect username")
    def test_user_attribute_email(self):
        self.assertEqual(self.user.email, "test_models_user@example.com", 
                                            "incorrect email")
    def test_user_attribute_password(self):
        self.assertTrue(check_password_hash(self.user.password, 
                                "test_models_user_pw"), "incorrect password")
    def test_user_attribute_joined_at(self):
        self.assertLess(self.user.joined_at, datetime.datetime.now(), 
                                                        "incorrect joined_at")
    def test_user_attribute_admin(self):
        self.assertFalse(self.user.is_admin, "incorrect admin")
        
    # def test_user_duplicate_username(self):
    #     try:
    #         models.User.create_user(
    #             username="test_models_user",
    #             email="totally_new_email@example.com",
    #             password="awesome_unique_password"
    #         )
    #     except:
    #         self.assertTrue(1)  #expect an exception will occur
    #     else:
    #         self.assertTrue(0)
    
    def test_user_duplicate_username(self):
        with self.assertRaises(ValueError):
            models.User.create_user(
                username="test_models_user",
                email="superUniqueEmail@example.com",
                password="superSecurePassword"
            )      
            
    def test_user_duplicate_email(self):
        with self.assertRaises(ValueError):
            models.User.create_user(
                username="test_models_user_2",
                email="test_models_user@example.com",
                password="test_models_user_pw"
            )
        
    
    def test_user_following(self):
        self.assertEqual(self.user.following(), self.user2, 
                                        "incorrect user following")
    def test_user_followers(self):
        self.assertEqual(self.user.followers(), self.user2,
                                        "incorrect user followers")
    def test_user_get_stream(self):
        with self.subTest(i=1):
            self.assertEqual(len(self.user.get_stream()), 2)   
        with self.subTest(i=2):
             self.assertEqual(len(self.user2.get_stream()), 1)   
        
    def test_user_get_posts(self):
        self.assertEqual(self.user.get_posts(), self.post, 
                                                "incorrect get_posts()")
         
#   POST TABLE TESTS  #

    def test_post_created(self):
        self.assertIsNotNone(self.post, "post was not created")
        
    def test_post_content(self):
        self.assertEqual(self.post.content, "test post content", 
                                            "incorrect post content")
    def test_post_timestamp(self):
        self.assertLess(self.post.timestamp, datetime.datetime.now(),
                                                "incorrect timestamp")

#   RELATIONSHIP TABLE TESTS  #

    def test_relationship_created(self):
        self.assertIsNotNone(self.relationship, "relationship was not created")
    
    def test_relationship_from_user(self):
        self.assertEqual(self.relationship.from_user, self.user, 
                                                    "incorrect from_user")
    def test_relationship_to_user(self):
        self.assertEqual(self.relationship.to_user, self.user2, 
                                                    "incorrect to_user")                                                    

if __name__ == '__main__':
    unittest.main()

#*** used for db clean-up if tearDown() fails   ***

    # for user in models.User.select():
    #     if user.username != "matt":
    #         models.User.delete().where(models.User.id==user.id).execute()
    #     print(user.username)
    
    # for post in models.Post.select():
    #     if post.content == "test post content 2":
    #         models.Post.delete().where(models.Post.id==post.id).execute()
    #     print('{}) {}'.format(post.id, post.content))