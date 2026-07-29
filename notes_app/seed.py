import random
from faker import Faker
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.note import Note

fake = Faker()

def seed_database():
    """Seed database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create sample users
        users = []
        sample_users = [
            {'username': 'alice', 'email': 'alice@example.com', 'password': 'Password123!'},
            {'username': 'bob', 'email': 'bob@example.com', 'password': 'Password123!'},
            {'username': 'carol', 'email': 'carol@example.com', 'password': 'Password123!'},
        ]
        
        for user_data in sample_users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create notes for each user
        categories = ['Personal', 'Work', 'Ideas', 'Projects', 'General']
        for user in users:
            for i in range(8):
                note = Note(
                    title=fake.sentence(nb_words=5),
                    content='\n\n'.join(fake.paragraphs(nb=3)),
                    category=random.choice(categories),
                    user_id=user.id
                )
                db.session.add(note)
        
        db.session.commit()
        
        print(f" Created {len(users)} users with notes")
        print(f" Total notes: {Note.query.count()}")
        print("\n Test Credentials:")
        for user in users:
            print(f"  • {user.username} / Password123!")

if __name__ == '__main__':
    seed_database()
