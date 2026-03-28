from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from flask_bcrypt import Bcrypt
from models import db, User
from datetime import datetime, timedelta
from functools import wraps
import re

bcrypt = Bcrypt()


# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validate_email(email):
    """Validate email format"""
    return EMAIL_REGEX.match(email) is not None


def validate_password(password):
    """
    Validate password strength
    Must be at least 8 characters
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, "Valid"


def validate_phone(phone):
    """
    Validate phone number (basic validation)
    """
    if not phone:
        return True  # Phone is optional

    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    # Check if it's 10-15 digits
    if not cleaned.isdigit() or len(cleaned) < 10 or len(cleaned) > 15:
        return False
    return True


def register_user(data):
    """
    Register a new user
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        # Extract data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        phone = data.get('phone', '').strip() if data.get('phone') else None
        full_name = data.get('full_name', '').strip() if data.get('full_name') else None
        age = data.get('age')

        # Validation
        if not username or not email or not password:
            return False, "Username, email, and password are required", None

        if len(username) < 3 or len(username) > 50:
            return False, "Username must be between 3 and 50 characters", None

        if not validate_email(email):
            return False, "Invalid email format", None

        valid_pw, pw_msg = validate_password(password)
        if not valid_pw:
            return False, pw_msg, None

        if phone and not validate_phone(phone):
            return False, "Invalid phone number format", None

        if age and (not isinstance(age, int) or age < 5 or age > 120):
            return False, "Age must be between 5 and 120", None

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return False, "Username already exists", None

        if User.query.filter_by(email=email).first():
            return False, "Email already registered", None

        if phone and User.query.filter_by(phone=phone).first():
            return False, "Phone number already registered", None

        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            phone=phone,
            full_name=full_name,
            age=age,
            role='user'
        )

        db.session.add(new_user)
        db.session.commit()

        return True, "User registered successfully", new_user.to_dict()

    except Exception as e:
        db.session.rollback()
        return False, f"Registration failed: {str(e)}", None


def login_user(data):
    """
    Login user and return JWT tokens
    Returns: (success: bool, message: str, tokens: dict or None, user_data: dict or None)
    """
    try:
        # Extract data
        username_or_email = data.get('username', '').strip().lower()
        password = data.get('password', '')

        if not username_or_email or not password:
            return False, "Username/email and password are required", None, None

        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user:
            return False, "Invalid credentials", None, None

        # Check if account is active
        if not user.is_active:
            return False, "Account is disabled. Please contact support.", None, None

        # Verify password
        if not bcrypt.check_password_hash(user.password_hash, password):
            return False, "Invalid credentials", None, None

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create JWT tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'username': user.username, 'role': user.role}
        )

        refresh_token = create_refresh_token(identity=user.id)

        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        return True, "User Login successful", tokens, user.to_dict()

    except Exception as e:
        return False, f"User Login failed: {str(e)}", None, None


def get_current_user():
    """
    Get current authenticated user from JWT token
    Must be called within a @jwt_required() route
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return user


def admin_required():
    """
    Decorator to require admin role
    Use after @jwt_required()
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user()
            if not user or user.role != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def update_user_profile(user_id, data):
    """
    Update user profile information
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found", None

        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name'].strip() if data['full_name'] else None

        if 'age' in data:
            age = data['age']
            if age and (not isinstance(age, int) or age < 5 or age > 120):
                return False, "Age must be between 5 and 120", None
            user.age = age

        if 'phone' in data:
            phone = data['phone'].strip() if data['phone'] else None
            if phone and not validate_phone(phone):
                return False, "Invalid phone number format", None

            # Check if phone is already used by another user
            if phone and User.query.filter(User.phone == phone, User.id != user_id).first():
                return False, "Phone number already in use", None

            user.phone = phone

        if 'profile_image' in data:
            user.profile_image = data['profile_image']

        db.session.commit()

        return True, "Profile updated successfully", user.to_dict()

    except Exception as e:
        db.session.rollback()
        return False, f"Update failed: {str(e)}", None


def change_password(user_id, old_password, new_password):
    """
    Change user password
    Returns: (success: bool, message: str)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        # Verify old password
        if not bcrypt.check_password_hash(user.password_hash, old_password):
            return False, "Current password is incorrect"

        # Validate new password
        valid_pw, pw_msg = validate_password(new_password)
        if not valid_pw:
            return False, pw_msg

        # Update password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        return True, "Password changed successfully"

    except Exception as e:
        db.session.rollback()
        return False, f"Password change failed: {str(e)}"


# Flask route handlers for authentication endpoints

def register_auth_routes(app):
    """
    Register authentication routes on Flask app
    """

    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        """User registration endpoint"""
        data = request.get_json()
        success, message, user_data = register_user(data)

        if success:
            return jsonify({
                "success": True,
                "message": message,
                "user": user_data
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """User login endpoint"""
        data = request.get_json()
        success, message, tokens, user_data = login_user(data)

        if success:
            return jsonify({
                "success": True,
                "message": message,
                "tokens": tokens,
                "user": user_data
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 401

    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def api_get_current_user():
        """Get current user info"""
        user = get_current_user()
        if user:
            return jsonify({
                "success": True,
                "user": user.to_dict()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

    @app.route('/api/auth/profile', methods=['PUT'])
    @jwt_required()
    def api_update_profile():
        """Update user profile"""
        user_id = get_jwt_identity()
        data = request.get_json()

        success, message, user_data = update_user_profile(user_id, data)

        if success:
            return jsonify({
                "success": True,
                "message": message,
                "user": user_data
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400

    @app.route('/api/auth/change-password', methods=['POST'])
    @jwt_required()
    def api_change_password():
        """Change user password"""
        user_id = get_jwt_identity()
        data = request.get_json()

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({
                "success": False,
                "error": "Both old and new passwords are required"
            }), 400

        success, message = change_password(user_id, old_password, new_password)

        if success:
            return jsonify({
                "success": True,
                "message": message
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400

    @app.route('/api/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def api_refresh_token():
        """Refresh access token"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_active:
            return jsonify({
                "success": False,
                "error": "Invalid user"
            }), 401

        access_token = create_access_token(
            identity=user.id,
            additional_claims={'username': user.username, 'role': user.role}
        )

        return jsonify({
            "success": True,
            "access_token": access_token
        }), 200

    print("✅ Authentication routes registered")
