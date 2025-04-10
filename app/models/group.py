# models/group.py
from app.extensions import db
from app.models.user_group import UserGroup

class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    group_users = db.relationship('UserGroup', back_populates='group', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='group', cascade='all, delete-orphan')

    def __init__(self, name: str, description: str = None) -> None:
        """Initialize a new group with name and optional description."""
        self.name = name
        self.description = description

    def add_member(self, user_id: int, role: int = 0) -> None:
        """Add a user to the group with specified role.
        Roles: 0=Member, 1=Admin, 2=Owner
        """
        membership = UserGroup(user_id=user_id, group_id=self.id, role=role)
        db.session.add(membership)

    def remove_member(self, user_id: int) -> None:
        """Remove a member from the group."""
        UserGroup.query.filter_by(group_id=self.id, user_id=user_id).delete()

    def update_role(self, user_id: int, new_role: int) -> None:
        """Change a member's role within the group."""
        membership = UserGroup.query.filter_by(group_id=self.id, user_id=user_id).first()
        membership.role = new_role

    def get_user_role(self, user_id: int) -> int | None:
        """Return the user's role in the group or None if not a member."""
        membership = UserGroup.query.filter_by(group_id=self.id, user_id=user_id).first()
        return membership.role if membership else None

    def is_owner(self, user_id: int) -> bool:
        """Check if user is the owner of the group."""
        return self.get_user_role(user_id) == 2

    @property
    def members(self) -> list['User | None']:
        """List of all members."""
        return [ug.user for ug in self.group_users]

    @property
    def admins(self) -> list['User | None']:
        """List of admin user."""
        return [ug.user for ug in self.group_users if ug.role == 1]



