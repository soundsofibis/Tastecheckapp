from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Usage tracking
    analyses_today = db.Column(db.Integer, default=0)
    last_analysis_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    def get_daily_limit(self):
        if self.is_admin:
            return float('inf')  # Unlimited
        elif self.is_premium:
            return float('inf')  # Unlimited
        else:
            return 10  # Free users
    
    def can_analyze(self):
        # Reset counter if new day
        today = datetime.utcnow().date()
        if self.last_analysis_date != today:
            self.analyses_today = 0
            self.last_analysis_date = today
            db.session.commit()
        
        return self.analyses_today < self.get_daily_limit()
    
    def increment_usage(self):
        self.analyses_today += 1
        db.session.commit()
