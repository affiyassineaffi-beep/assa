"""SQLAlchemy models for the Academic Platform."""
from __future__ import annotations
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False, default="")
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    auth_provider = db.Column(db.String(32), nullable=False, default="password")
    phone = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(16), nullable=True)        # 'female' | 'male' | 'other'
    custom_theme = db.Column(db.Text, nullable=True)        # JSON: AI-generated theme tokens

    # Account activation & verification
    is_active = db.Column(db.Integer, nullable=False, default=0)
    email_verified = db.Column(db.Integer, nullable=False, default=0)
    email_verify_token = db.Column(db.String(80), nullable=True, index=True)
    phone_verified = db.Column(db.Integer, nullable=False, default=0)
    phone_otp = db.Column(db.String(8), nullable=True)
    phone_otp_expires = db.Column(db.DateTime, nullable=True)

    educational_level = db.Column(db.String(60), nullable=True)
    section = db.Column(db.String(60), nullable=True)
    region_city = db.Column(db.String(120), nullable=True)
    school_name = db.Column(db.String(255), nullable=True)
    class_section = db.Column(db.String(60), nullable=True)
    profile_completed = db.Column(db.Integer, nullable=False, default=0)

    # User preferences
    theme = db.Column(db.String(16), nullable=False, default="dark")        # dark | light | system
    language = db.Column(db.String(8), nullable=False, default="fr")        # fr | ar | en

    # Gamification
    points = db.Column(db.Integer, nullable=False, default=0)               # lifetime XP
    level = db.Column(db.Integer, nullable=False, default=1)
    experience = db.Column(db.Integer, nullable=False, default=0)           # XP within current level
    reputation = db.Column(db.Integer, nullable=False, default=0)           # upvotes / kudos
    badge_icon = db.Column(db.String(8), nullable=True)                     # 🥉 🥈 🥇 💎 🏆

    # Profile picture (uploaded path or remote URL — incl. Google avatar)
    avatar_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    grades = db.relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    sent_messages = db.relationship("Message", foreign_keys="Message.sender_id",
                                    back_populates="sender", cascade="all, delete-orphan")
    received_messages = db.relationship("Message", foreign_keys="Message.recipient_id",
                                        back_populates="recipient", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "school_name": self.school_name,
            "educational_level": self.educational_level,
            "section": self.section,
            "region_city": self.region_city,
            "avatar_url": self.avatar_url,
            "points": self.points,
            "level": self.level,
            "badge_icon": self.badge_icon,
        }


class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    note = db.Column(db.Float, nullable=False)
    coefficient = db.Column(db.Float, nullable=False, default=1.0)
    is_optional = db.Column(db.Integer, nullable=False, default=0)
    is_public = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="grades")


class Track(db.Model):
    """A playlist item — either a hosted audio file or a YouTube link."""
    __tablename__ = "tracks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    kind = db.Column(db.String(16), nullable=False, default="youtube")  # 'youtube' | 'audio'
    source = db.Column(db.String(500), nullable=False)  # YouTube ID OR /static/uploads/... path
    playlist = db.Column(db.String(80), nullable=False, default="Study Tracks")
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "kind": self.kind,
            "source": self.source,
            "playlist": self.playlist,
            "position": self.position,
        }


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    # For DMs: recipient_id is the peer. For group messages: recipient_id == sender_id (placeholder)
    # and group_id is set. Use group_id IS NULL to filter for DMs.
    recipient_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id", ondelete="CASCADE"), nullable=True, index=True)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Integer, nullable=False, default=0)
    seen_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("Student", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient = db.relationship("Student", foreign_keys=[recipient_id], back_populates="received_messages")

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "group_id": self.group_id,
            "body": self.body,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "seen_at": self.seen_at.isoformat() if self.seen_at else None,
        }


class Group(db.Model):
    """A group chat — typically created for a class or specialty."""
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(280), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship("GroupMember", back_populates="group",
                              cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description,
                "owner_id": self.owner_id}


class GroupMember(db.Model):
    __tablename__ = "group_members"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id", ondelete="CASCADE"),
                         nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    role = db.Column(db.String(16), nullable=False, default="member")    # owner | admin | member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    group = db.relationship("Group", back_populates="members")
    student = db.relationship("Student", foreign_keys=[student_id])

    __table_args__ = (db.UniqueConstraint("group_id", "student_id", name="uq_group_member"),)


class Resource(db.Model):
    """Student-shared study resource: PDF upload, summary text, or external link."""
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    kind = db.Column(db.String(16), nullable=False, default="file")     # 'file' | 'text' | 'link'
    file_path = db.Column(db.String(500), nullable=True)                 # /static/uploads/resources/...
    link_url = db.Column(db.String(500), nullable=True)
    body = db.Column(db.Text, nullable=True)                             # for 'text' kind (summaries)
    subject = db.Column(db.String(120), nullable=True)
    educational_level = db.Column(db.String(60), nullable=True)
    institution = db.Column(db.String(255), nullable=True)               # auto-filled from author school
    upvotes = db.Column(db.Integer, nullable=False, default=0)
    downloads = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", foreign_keys=[student_id])

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "kind": self.kind,
            "file_path": self.file_path,
            "link_url": self.link_url,
            "body": self.body,
            "subject": self.subject,
            "educational_level": self.educational_level,
            "institution": self.institution,
            "upvotes": self.upvotes,
            "downloads": self.downloads,
            "author_id": self.student_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
