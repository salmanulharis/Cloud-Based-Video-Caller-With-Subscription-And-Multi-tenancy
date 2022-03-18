from functools import wraps
from flask_login import current_user
from app.models import UserRoles, Role
from flask import abort

# Defining our custom decorator
def access_level(level_list):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            role = UserRoles.query.filter_by(user_id=current_user.id).first()
            user_role = Role.query.filter_by(id=role.role_id).first()
            if not user_role.name in level_list:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator