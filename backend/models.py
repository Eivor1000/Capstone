"""
Database Models for AI Creative Suite
Uses SQLAlchemy ORM with PostgreSQL
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()


class User(db.Model):
    """User authentication and profile"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    profile_image = db.Column(db.Text)
    role = db.Column(db.String(20), default='user')  # 'user', 'parent', 'teacher', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    stories = db.relationship('Story', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    study_sessions = db.relationship('StudySession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    kids_submissions = db.relationship('KidsSubmission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    video_searches = db.relationship('VideoSearch', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'full_name': self.full_name,
            'age': self.age,
            'profile_image': self.profile_image,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }


class Story(db.Model):
    """Generated stories with cover images"""
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200))
    prompt = db.Column(db.Text, nullable=False)
    story_text = db.Column(db.Text, nullable=False)
    cover_image_data = db.Column(db.Text)  # Base64 encoded
    word_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_favorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Story {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'prompt': self.prompt,
            'story_text': self.story_text,
            'cover_image_data': self.cover_image_data,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_favorite': self.is_favorite,
        }


class StudySession(db.Model):
    """Study assistant sessions (summaries and explanations)"""
    __tablename__ = 'study_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    topic = db.Column(db.String(200), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    mode = db.Column(db.String(20), nullable=False, index=True)  # 'summarize' or 'explain'
    output_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    video_searches = db.relationship('VideoSearch', backref='study_session', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<StudySession {self.id}: {self.mode} - {self.topic}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'input_text': self.input_text,
            'mode': self.mode,
            'output_text': self.output_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Quiz(db.Model):
    """Generated quizzes (MCQs and Q&As)"""
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    topic = db.Column(db.String(200), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    mcqs = db.Column(JSON, nullable=False)  # Array of MCQ objects
    qas = db.Column(JSON, nullable=False)   # Array of Q&A objects
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Quiz {self.id}: {self.topic}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'input_text': self.input_text,
            'mcqs': self.mcqs,
            'qas': self.qas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class QuizAttempt(db.Model):
    """User's quiz attempt results"""
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    mcq_score = db.Column(db.Integer)  # Number correct
    mcq_total = db.Column(db.Integer)  # Total questions
    answers = db.Column(JSON)  # User's answers
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<QuizAttempt {self.id}: Quiz {self.quiz_id} - {self.mcq_score}/{self.mcq_total}>'

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'mcq_score': self.mcq_score,
            'mcq_total': self.mcq_total,
            'answers': self.answers,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class KidsAssignment(db.Model):
    """Kids creative challenge assignments"""
    __tablename__ = 'kids_assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'coloring', 'drawing', 'craft'
    difficulty = db.Column(db.String(20), nullable=False)  # 'easy', 'medium', 'hard'
    criteria = db.Column(db.Text, nullable=False)
    points_possible = db.Column(db.Integer, default=100)
    image_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    submissions = db.relationship('KidsSubmission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<KidsAssignment {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'difficulty': self.difficulty,
            'criteria': self.criteria,
            'points_possible': self.points_possible,
            'image_url': self.image_url,
            'active': self.is_active,
        }


class KidsSubmission(db.Model):
    """Kids creative challenge submissions with AI grading"""
    __tablename__ = 'kids_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('kids_assignments.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Parent's account (optional)
    child_name = db.Column(db.String(50), nullable=False, index=True)
    image_data = db.Column(db.Text)  # Base64 (optional storage)
    image_url = db.Column(db.Text)   # Or URL to stored image
    score = db.Column(db.Numeric(3, 1), nullable=False)  # 0.0 to 10.0
    points_earned = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    improvement = db.Column(db.Text)
    vision_description = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    week = db.Column(db.String(10), index=True)  # Format: YYYY-WXX

    def __repr__(self):
        return f'<KidsSubmission {self.id}: {self.child_name} - {self.score}/10>'

    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'user_id': self.user_id,
            'child_name': self.child_name,
            'image_url': self.image_url,
            'score': float(self.score) if self.score else 0,
            'points_earned': self.points_earned,
            'feedback': self.feedback,
            'improvement': self.improvement,
            'vision_description': self.vision_description,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'week': self.week,
        }


class VideoSearch(db.Model):
    """Educational video search history"""
    __tablename__ = 'video_searches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'), nullable=True)
    input_text = db.Column(db.Text, nullable=False)
    extracted_topic = db.Column(db.String(200), nullable=False)
    videos = db.Column(JSON, nullable=False)  # Array of video objects
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<VideoSearch {self.id}: {self.extracted_topic}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'study_session_id': self.study_session_id,
            'input_text': self.input_text,
            'extracted_topic': self.extracted_topic,
            'videos': self.videos,
            'searched_at': self.searched_at.isoformat() if self.searched_at else None,
        }
