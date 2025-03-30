# models/group.py
from app.extensions import db
from app.models.user_group import UserGroup

class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    def __init__(self, name: str, description: str) -> None:
        """Initializes a group with validated inputs from forms/database constraints."""
        self.name = name
        self.description = description

    @classmethod
    def create(cls, name: str, description: str, owner_id: int) -> 'Group':
        """Creates a group and atomically assigns ownership. Returns the new group."""
        group = cls(name=name, description=description)
        db.session.add(group)
        db.session.flush()
        UserGroup.add_member(group.id, owner_id, role=2)  # Owner assignment is atomic
        db.session.commit()
        return group

    def delete(self, requester_id: int) -> bool:
        """Deletes group only if requester is the owner."""
        if not self.is_owner(requester_id):
            return False
        UserGroup.query.filter_by(group_id=self.id).delete()
        db.session.delete(self)
        db.session.commit()
        return True

    def add_member(self, user_id: int, role: int = 0) -> bool:
        """Adds a user to the group with a role (0=member, 1=admin, 2=owner). Returns success status."""
        return UserGroup.add_member(self.id, user_id, role)

    def remove_member(self, user_id: int, requester_id: int) -> bool:
        """Delegates to UserGroup for permission checks and removal."""
        return UserGroup.remove_member(self.id, user_id, requester_id)

    def update_role(self, user_id: int, new_role: int, requester_id: int) -> bool:
        """Delegates to UserGroup for permission checks and role updates."""
        return UserGroup.update_role(self.id, user_id, new_role, requester_id)

    def is_member(self, user_id: int) -> bool:
        """Checks if a user is a member of this group."""
        return user_id in self.members

    def is_admin(self, user_id: int) -> bool:
        """Checks if a user is an admin of this group."""
        return user_id in self.admins

    def is_owner(self, user_id: int) -> bool:
        """Checks if a user is the owner of this group."""
        return self.owner == user_id

    @property
    def members(self) -> list[int]:
        """Returns all member user IDs. Used for membership listings and bulk actions."""
        return [ug.user_id for ug in UserGroup.query.filter_by(group_id=self.id).all()]

    @property
    def admins(self) -> list[int]:
        """Returns admin user IDs. Drives permission checks for group management."""
        return [ug.user_id for ug in UserGroup.query.filter_by(group_id=self.id, role=1).all()]

    @property
    def owner(self) -> int:
        """Returns owner's user ID. Critical for ownership verification workflows."""
        return UserGroup.query.filter_by(group_id=self.id, role=2).first().user_id

