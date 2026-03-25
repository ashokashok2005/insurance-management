from app import create_app, db
from app.models import Agent

app = create_app()

with app.app_context():
    email = 'ashokarun301105@gmail.com'
    agent = Agent.query.filter_by(email=email).first()
    
    if agent:
        print(f"User {email} found.")
        agent.set_password('admin123')
        agent.role = 'admin'
        agent.is_active = True
        print("Password reset to: admin123")
        print("Role set to: admin")
    else:
        print(f"User {email} NOT found. Creating...")
        agent = Agent(email=email, name='Admin User', role='admin', is_active=True)
        agent.set_password('admin123')
        db.session.add(agent)
        print("User created. Password: admin123")
    
    db.session.commit()
    print("Done.")
