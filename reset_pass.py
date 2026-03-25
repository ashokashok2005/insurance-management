from app import db, create_app
from app.models import Agent

app = create_app()
with app.app_context():
    agent = Agent.query.filter_by(email='test@demo.com').first()
    if agent:
        print(f"Resetting password for {agent.email}...")
        agent.set_password('123456')
        db.session.commit()
        print("Password reset successful.")
    else:
        print("Agent test@demo.com not found.")
