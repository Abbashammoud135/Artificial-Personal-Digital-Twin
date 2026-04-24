from models.role import Role
from sqlalchemy.orm import Session


def seed_roles(session: Session):
    """Seed default roles into the database"""
    
    # Check if roles already exist
    role_count = session.query(Role).count()

    if role_count == 0:
        roles = [
            Role(name="user", description="Dashboard user with limited access"),
            Role(name="agent", description="Internal system agent"),
            Role(name="admin", description="Full system access")
        ]
        
        session.add_all(roles)
        session.commit()
        print("✔ Roles seeded")
    else:
        print("✔ Roles already exist")