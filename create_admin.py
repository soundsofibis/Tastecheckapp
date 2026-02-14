from app import app, db, bcrypt
from models import User

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='ian@tastecheck.com').first()
    
    if not admin:
        # Create admin account
        hashed_password = bcrypt.generate_password_hash('ChangeThisPassword123!').decode('utf-8')
        admin = User(
            email='ian@tastecheck.com',
            password_hash=hashed_password,
            is_admin=True,
            is_premium=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin account created: ian@tastecheck.com")
        print("⚠️  Password: ChangeThisPassword123!")
        print("🔒 CHANGE THIS PASSWORD IMMEDIATELY after first login!")
    else:
        print("Admin account already exists")
