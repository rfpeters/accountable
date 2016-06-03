#Accountable Politics
#test_db_cleanup.py

import models

print("***** USERS *****")
for user in models.User.select():
    print(user.username)
    ans = input("> delete: yN ")
    if ans == "y":
        models.User.delete().where(models.User.id==user.id).execute()
        
print("***** POSTS *****")
for post in models.Post.select():
    print('{}) {}'.format(post.id, post.content))    
    ans = input("> delete: yN ")
    if ans == "y":
        models.Post.delete().where(models.Post.id==post.id).execute()   