"""
Database Configuration and Helper Functions
"""

from models import db, User, KidsAssignment
from flask_bcrypt import Bcrypt
import os

bcrypt = Bcrypt()


def init_database(app):
    """
    Initialize database with app
    """
    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")

        # Seed initial data
        seed_kids_assignments()

    return db


def seed_kids_assignments():
    """
    Seed initial kids challenge assignments if table is empty
    """
    if KidsAssignment.query.count() == 0:
        print("📝 Seeding initial kids assignments...")

        assignments = [
            {
                "title": "Rainbow Coloring",
                "description": "Color a beautiful rainbow with all 7 colors! Be creative and use bright colors.",
                "type": "coloring",
                "difficulty": "easy",
                "points_possible": 100,
                "criteria": "Use all 7 rainbow colors (red, orange, yellow, green, blue, indigo, violet). Stay within the lines. Use bright, vibrant colors.",
                "image_url": "https://via.placeholder.com/400x300?text=Rainbow+Template",
                "is_active": True
            },
            {
                "title": "Paper Plate Fish",
                "description": "Create a colorful fish using a paper plate, colors, and decorations!",
                "type": "craft",
                "difficulty": "medium",
                "points_possible": 100,
                "criteria": "Use a paper plate as the fish body. Add fins and tail. Decorate with colors, patterns, or glitter. Be creative!",
                "image_url": "https://via.placeholder.com/400x300?text=Fish+Example",
                "is_active": True
            },
            {
                "title": "Draw Your Dream House",
                "description": "Draw the house of your dreams! What would it look like?",
                "type": "drawing",
                "difficulty": "medium",
                "points_possible": 100,
                "criteria": "Include doors, windows, and a roof. Add colors and details. Be imaginative!",
                "image_url": "https://via.placeholder.com/400x300?text=House+Example",
                "is_active": True
            },
            {
                "title": "Handprint Art",
                "description": "Create art using your handprints! Make animals, flowers, or anything you imagine!",
                "type": "craft",
                "difficulty": "easy",
                "points_possible": 100,
                "criteria": "Use your handprints creatively. Add details with markers or crayons. Make it colorful!",
                "image_url": "https://via.placeholder.com/400x300?text=Handprint+Art",
                "is_active": True
            },
            {
                "title": "Underwater Scene",
                "description": "Draw an underwater world with fish, coral, and sea creatures!",
                "type": "drawing",
                "difficulty": "medium",
                "points_possible": 100,
                "criteria": "Include at least 3 sea creatures. Add coral, seaweed, or rocks. Use blue and ocean colors.",
                "image_url": "https://via.placeholder.com/400x300?text=Underwater+Scene",
                "is_active": True
            }
        ]

        for assignment_data in assignments:
            assignment = KidsAssignment(**assignment_data)
            db.session.add(assignment)

        db.session.commit()
        print(f"✅ Seeded {len(assignments)} kids assignments!")
    else:
        print("ℹ️  Kids assignments already exist, skipping seed.")


def create_test_user():
    """
    Create a test user for development
    """
    test_email = "test@example.com"

    if not User.query.filter_by(email=test_email).first():
        print("👤 Creating test user...")

        test_user = User(
            username="testuser",
            email=test_email,
            phone="1234567890",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
            full_name="Test User",
            age=25,
            role="user"
        )

        db.session.add(test_user)
        db.session.commit()

        print("✅ Test user created!")
        print("   Username: testuser")
        print("   Email: test@example.com")
        print("   Password: password123")
    else:
        print("ℹ️  Test user already exists.")


def get_database_url():
    """
    Get database URL from environment variables
    """
    # Option 1: Full DATABASE_URL
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        # Fix for Heroku postgres:// -> postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url

    # Option 2: Individual components
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ai_creative_suite')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')

    return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'


def reset_database(app):
    """
    WARNING: Drops all tables and recreates them
    Only use in development!
    """
    with app.app_context():
        print("⚠️  WARNING: Dropping all tables...")
        db.drop_all()
        print("✅ All tables dropped!")

        print("📝 Recreating tables...")
        db.create_all()
        print("✅ Tables recreated!")

        seed_kids_assignments()
        create_test_user()

        print("✅ Database reset complete!")
