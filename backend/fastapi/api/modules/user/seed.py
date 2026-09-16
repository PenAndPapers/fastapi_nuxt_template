import uuid

from sqlalchemy.orm import Session

from api.modules.auth.password.service import PasswordService
from api.modules.user.model import Permission, Role, RolePermission, User, UserRole


def seed_rbac_data(db: Session) -> None:
  # 1. Define Basic Permissions
  # Format: {name: description}
  permissions_data = {
    "all": "Full access to everything",
    "user:read": "Read user data",
    "user:write": "Modify user data",
    "user:delete": "Delete user data",
    "content:read": "Read content",
    "content:write": "Create/Edit content",
    "content:publish": "Publish content",
    "content:delete": "Delete content",
  }

  permission_objs = {}
  for name, desc in permissions_data.items():
    perm = db.query(Permission).filter_by(name=name).first()
    if not perm:
      perm = Permission(name=name, description=desc)
      db.add(perm)
      db.flush()
    permission_objs[name] = perm

  # 2. Define Roles and map to Permissions
  # SuperAdmin: All
  # Admin: All except maybe some system settings (for this demo, all)
  # Editor: content:read, content:write
  # Publisher: content:read, content:write, content:publish
  # User: user:read, content:read
  roles_config = {
    "SuperAdmin": ["all"],
    "Admin": [
      "user:read",
      "user:write",
      "user:delete",
      "content:read",
      "content:write",
      "content:publish",
      "content:delete",
    ],
    "Editor": ["content:read", "content:write"],
    "Publisher": ["content:read", "content:write", "content:publish"],
    "User": ["user:read", "content:read"],
  }

  role_objs = {}
  for role_name, perms_list in roles_config.items():
    role = db.query(Role).filter_by(name=role_name).first()
    if not role:
      role = Role(name=role_name, description=f"Role for {role_name}")
      db.add(role)
      db.flush()
    role_objs[role_name] = role

    # Map Permissions to Role
    for p_name in perms_list:
      perm = permission_objs[p_name]
      exists = db.query(RolePermission).filter_by(role_id=role.id, permission_id=perm.id).first()
      if not exists:
        db.add(RolePermission(role_id=role.id, permission_id=perm.id))

  # 3. Create Sample Users
  # we use a dummy password "password123" - in real use, password service hashes it
  pw_service = PasswordService()

  users_to_create = [
    {"email": "superadmin@example.com", "username": "superadmin", "role": "SuperAdmin"},
    {"email": "admin@example.com", "username": "admin", "role": "Admin"},
    {"email": "editor@example.com", "username": "editor", "role": "Editor"},
    {"email": "publisher@example.com", "username": "publisher", "role": "Publisher"},
    {"email": "user@example.com", "username": "user", "role": "User"},
  ]

  for u_data in users_to_create:
    user = db.query(User).filter_by(email=u_data["email"]).first()
    hashed_pw = pw_service.password_hash("password123")
    if not user:
      user = User(
        uuid=str(uuid.uuid4()),
        email=u_data["email"],
        password=hashed_pw,
        first_name=u_data["username"].title(),
        last_name="Sample",
      )
      db.add(user)
      db.flush()

    # Assign Role to User
    role = role_objs[u_data["role"]]
    exists = db.query(UserRole).filter_by(user_id=user.id, role_id=role.id).first()
    if not exists:
      db.add(UserRole(user_id=user.id, role_id=role.id))

  db.commit()

  print("RBAC Seed data created successfully.")
