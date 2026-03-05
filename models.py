from auth import validate_token

class User:
    def __init__(self, name):
        self.name = name

class Admin(User):
    def delete_user(self, user_id):
        if validate_token("some_token"):
            print(f"Deleting user {user_id}")
