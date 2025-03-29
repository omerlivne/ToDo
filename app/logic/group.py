# logic/group.py
from app.extensions import db
from app.models import Group, UserGroup


def create_group(name: str, description: str, requester_username: str) -> Group | None:
    """Create a new group with validation"""
    if not name:
        return None # empty name

    group = Group(name, description, requester_username)
    db.session.add(group)
    db.session.commit()
    add_member(group, requester_username, True)
    return group

def delete_group(group: Group, requester_username: str) -> bool:
    """Delete group only if requester is the owner"""
    if group.owner != requester_username:
        return False

    UserGroup.query.filter_by(group_id=group.id).delete()
    db.session.delete(group)
    db.session.commit()
    return True

def add_member(group: Group, username: str, admin: bool = False) -> bool:
    """Add member with authorization checks"""
    if UserGroup.query.filter_by(group_id=group.id, user_id=username).first():
        return False
    user_group = UserGroup(user_id=username, group_id=group.id, admin=admin)
    db.session.add(user_group)
    db.session.commit()
    return True


def add_member(group: Group, requester_username: str,  new_member_username: str, admin: bool = False) -> bool:
    """Add member with authorization checks"""
    # Check permissions
    if not (is_group_owner(group, requester_username) or is_group_admin(group, requester_username)):
        return False

    # Validate user exists
    if not User.query.get(new_member_username):
        return False

    # Prevent duplicates
    if UserGroup.query.filter_by(group_id=group.id, user_id=new_member_username).first():
        return False

    user_group = UserGroup(user_id=new_member_username, group_id=group.id, admin=admin)
    db.session.add(user_group)
    db.session.commit()
    return True

def remove_member(group: Group, username: str) -> bool:
    """Remove user from group"""
    user_group = UserGroup.query.filter_by(group_id=group.id, user_id=username).first()
    if not user_group:
        return False
    db.session.delete(user_group)
    db.session.commit()
    return True

def is_group_admin(group: Group, username: str) -> bool:
    """Check if user is group admin"""
    user_group = UserGroup.query.filter_by(group_id=group.id, user_id=username).first()
    return user_group and user_group.admin

