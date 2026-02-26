"""User repository — database interaction only, no business logic."""

from models import db
from models.user import User, UserRole


def get_by_firebase_uid(firebase_uid):
    """Return a User by Firebase UID, or None."""
    return User.query.filter_by(firebase_uid=firebase_uid).first()


def get_by_employee_id(employee_id):
    """Return a User by their employee_id string (e.g. 'EMP-001'), or None."""
    return User.query.filter_by(employee_id=employee_id).first()


def get_by_id(user_id):
    """Return a User by primary key, or None."""
    return db.session.get(User, user_id)


def get_all_employees():
    """Return all users with role EMPLOYEE."""
    return User.query.filter_by(role=UserRole.EMPLOYEE).all()


def create(firebase_uid, email, role=UserRole.EMPLOYEE):
    """Create a new User with an auto-generated employee_id."""
    employee_id = _generate_employee_id()
    user = User(
        firebase_uid=firebase_uid,
        email=email,
        role=role,
        employee_id=employee_id,
    )
    db.session.add(user)
    db.session.commit()
    return user


def _generate_employee_id():
    """Generate the next employee ID like EMP-001, EMP-002, etc."""
    last_user = User.query.order_by(User.id.desc()).first()
    next_num = (last_user.id + 1) if last_user else 1
    return f"EMP-{next_num:03d}"
