from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'jobseeker' or 'recruiter'
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_password_change = db.Column(db.DateTime, default=datetime.utcnow)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Relationships
    jobseeker_profile = db.relationship('JobSeekerProfile', backref='user', uselist=False)
    recruiter_profile = db.relationship('RecruiterProfile', backref='user', uselist=False)
    password_history = db.relationship('PasswordHistory', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.utcnow()
        
        # Add to password history
        history = PasswordHistory(
            user_id=self.id,
            password_hash=self.password_hash
        )
        db.session.add(history)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def check_password_expired(self):
        """Check if password is older than 30 days (Naukri's policy)"""
        if self.last_password_change:
            days_since_change = (datetime.utcnow() - self.last_password_change).days
            return days_since_change >= 30
        return True
    
    def can_use_password(self, new_password):
        """Check if password was used before (no repetition rule)"""
        # Check against current password
        if self.check_password(new_password):
            return False
        
        # Check against last password (Naukri's policy: cannot be same as immediate previous)
        last_password = self.password_history.order_by(PasswordHistory.created_at.desc()).first()
        if last_password and check_password_hash(last_password.password_hash, new_password):
            return False
        
        return True
    
    def increment_login_attempts(self):
        """Track failed login attempts"""
        self.login_attempts += 1
        if self.login_attempts >= 5:  # Max 5 attempts
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
    
    def reset_login_attempts(self):
        """Reset login attempts on successful login"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
        db.session.commit()

class PasswordHistory(db.Model):
    __tablename__ = 'password_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobSeekerProfile(db.Model):
    __tablename__ = 'jobseeker_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    # Personal Information
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photo = db.Column(db.String(200))  # Path to photo
    
    # Professional Information (Fresher specific)
    is_fresher = db.Column(db.Boolean, default=True)
    current_employer = db.Column(db.String(100))  # "Not Applicable" for freshers
    current_designation = db.Column(db.String(100))  # "Not Applicable" for freshers
    
    # Education
    highest_qualification = db.Column(db.String(100))
    college_name = db.Column(db.String(200))
    graduation_year = db.Column(db.Integer)
    specialization = db.Column(db.String(100))
    
    # Skills
    key_skills = db.Column(db.Text)  # Comma-separated skills
    
    # Resume
    resume_path = db.Column(db.String(200))
    resume_filename = db.Column(db.String(200))
    resume_uploaded_at = db.Column(db.DateTime)
    
    # Profile Settings
    profile_visibility = db.Column(db.String(20), default='visible')  # visible, hidden
    blocked_companies = db.Column(db.Text)  # JSON list of blocked company IDs
    
    # Profile completion
    profile_completion_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_completion_percentage(self):
        """Calculate profile completion percentage"""
        percentage = 0
        fields = [
            self.full_name, self.phone, self.date_of_birth, self.gender,
            self.highest_qualification, self.college_name, self.graduation_year,
            self.specialization, self.key_skills
        ]
        
        # Count filled fields
        filled = sum(1 for field in fields if field)
        percentage = (filled / len(fields)) * 100
        
        # Bonus for photo
        if self.photo:
            percentage += 10  # Photo boost
        
        return min(100, int(percentage))
    
    def get_visibility_status(self):
        """Get profile visibility status with recruiter boost info"""
        return {
            'visibility': self.profile_visibility,
            'photo_boost': 40 if self.photo else 0,  # 40% more likely to be contacted
            'completion': self.calculate_completion_percentage()
        }

class RecruiterProfile(db.Model):
    __tablename__ = 'recruiter_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    # Company Information
    company_name = db.Column(db.String(200), nullable=False)
    company_email = db.Column(db.String(120), nullable=False)
    company_phone = db.Column(db.String(15), nullable=False)
    company_address = db.Column(db.Text)
    company_website = db.Column(db.String(200))
    
    # Recruiter Information
    recruiter_name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    
    # Verification Documents (KYC)
    pan_number = db.Column(db.String(20))
    pan_document = db.Column(db.String(200))
    address_proof = db.Column(db.String(200))
    is_kyc_verified = db.Column(db.Boolean, default=False)
    
    # Subscription
    subscription_type = db.Column(db.String(50), default='free')  # free, basic, premium
    subscription_expiry = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='recruiter', lazy='dynamic')

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id'))
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    experience_required = db.Column(db.String(50))
    
    # Job type
    is_featured = db.Column(db.Boolean, default=False)  # Sponsored/promoted jobs
    job_type = db.Column(db.String(50))  # full-time, part-time, contract
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Applications
    applications = db.relationship('JobApplication', backref='job', lazy='dynamic')

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    jobseeker_id = db.Column(db.Integer, db.ForeignKey('jobseeker_profiles.id'))
    
    # Application details
    cover_letter = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='applied')  # applied, shortlisted, rejected, hired
    
    # Recruiter actions
    recruiter_notes = db.Column(db.Text)
    viewed_at = db.Column(db.DateTime)
    
    # Ensure one application per job per user
    __table_args__ = (
        db.UniqueConstraint('job_id', 'jobseeker_id', name='unique_application'),
    )

class OTPVerification(db.Model):
    __tablename__ = 'otp_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    otp = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50))  # registration, password_reset, email_verify
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at

class BlockedCompany(db.Model):
    __tablename__ = 'blocked_companies'
    
    id = db.Column(db.Integer, primary_key=True)
    jobseeker_id = db.Column(db.Integer, db.ForeignKey('jobseeker_profiles.id'))
    company_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)