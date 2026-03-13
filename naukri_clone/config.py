import os
from datetime import timedelta

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'jobs.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security configurations
    SECRET_KEY = 'your-secret-key-here-change-in-production'  # Change in production
    SECURITY_PASSWORD_SALT = 'your-password-salt-change-in-production'
    
    # Password policy - Following Naukri's 30-day rule
    PASSWORD_EXPIRY_DAYS = 30
    PASSWORD_HISTORY_COUNT = 1  # Cannot reuse last password
    
    # Session configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'resumes')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'rtf'}
    
    # Profile completion requirements
    PROFILE_COMPLETION_PERCENTAGE = 100
    PHOTO_BOOST_PERCENTAGE = 40  # 40% more likely to get contacted with photo
    
    # Rate limiting for security
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME_MINUTES = 15
    
    # Email configuration (for OTP)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'  # Configure this
    MAIL_PASSWORD = 'your-app-password'      # Configure this