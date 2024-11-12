# users.py
users = {
    "manager_user": {"username": "manager_user", "role": "manager"},
    "manager_user1": {"username": "manager_user1", "role": "manager"},
    "admin_user": {"username": "admin_user", "role": "admin"},
    "normal_user": {"username": "normal_user", "role": "normal"}
}

def get_user(username):
    return users.get(username)
