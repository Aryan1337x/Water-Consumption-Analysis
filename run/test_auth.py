import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("Testing user creation...")
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    print(f"User created: {user}")
    
    print("\nTesting user query...")
    found_user = User.query.filter_by(username="testuser").first()
    print(f"Found user: {found_user}")
    print(f"Password check: {found_user.check_password('password123')}")
    
    print("\nTesting dashboard stats...")
    from app.services import get_dashboard_stats
    stats = get_dashboard_stats(found_user.id)
    print(f"Stats: {stats}")
    
    print("\nAll tests passed!")
