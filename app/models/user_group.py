# models/user_group.py
from app.extensions import db

class UserGroup(db.Model):
    __tablename__ = "users_groups"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    role = db.Column(db.Integer, nullable=False, default=0)  # 0=member, 1=admin, 2=owner

    @classmethod
    def add_member(cls, group_id: int, user_id: int, role: int = 0) -> bool:
        """Adds a user to a group with a role. Fails if user is already a member."""
        if cls.get_ug(group_id, user_id):
            return False
        ug = cls(user_id=user_id, group_id=group_id, role=role)
        db.session.add(ug)
        db.session.commit()
        return True

    @classmethod
    def remove_member(cls, group_id: int, user_id: int, requester_id: int) -> bool:
        """Removes a member if requester is the owner/admin and not removing themselves."""
        target_ug = cls.get_ug(group_id, user_id)
        requester_ug = cls.get_ug(group_id, requester_id)

        # Block invalid requests or self-removal
        if not target_ug or not requester_ug or user_id == requester_id:
            return False

        # Owners can remove anyone; admins can remove members (not admins)
        if requester_ug.role == 2 or (requester_ug.role == 1 and target_ug.role == 0):
            db.session.delete(target_ug)
            db.session.commit()
            return True
        return False

    @classmethod
    def update_role(cls, group_id: int, user_id: int, new_role: int, requester_id: int) -> bool:
        """Updates a member's role if requester is the owner and not modifying themselves."""
        if cls.get_role(group_id, requester_id) != 2 or user_id == requester_id:
            return False  # Block non-owners or self-changes

        ug = cls.get_ug(group_id, user_id)
        if not ug:
            return False

        ug.role = new_role
        db.session.commit()
        return True

    @classmethod
    def get_ug(cls, group_id: int, user_id: int) -> 'UserGroup | None':
        """Returns the UserGroup relationship if it exists."""
        return cls.query.filter_by(group_id=group_id, user_id=user_id).first()

    @classmethod
    def get_role(cls, group_id: int, user_id: int) -> int | None:
        """Returns the user's role in the group, or `None` if not a member."""
        ug = cls.get_ug(group_id, user_id)
        return ug.role if ug else None

