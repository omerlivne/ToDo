# models/group.py
from app.extensions import db
from app.models.user_group import UserGroup

class Group(db.Model):

    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    owner = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner = owner

    @property
    def members(self):
        return [ug.user_id for ug in UserGroup.query.filter_by(group_id=self.id).all()]

    @property
    def admins(self):
        return [ug.user_id for ug in UserGroup.query.filter_by(group_id=self.id, admin=True).all()]