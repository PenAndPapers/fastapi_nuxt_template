from sqlalchemy.orm import Session

from api.modules.auth.password.service import PasswordService
from api.modules.user.model import Permission, Role, RolePermission, User, UserRole
from api.modules.user.schema import EnumUserPermission, EnumUserRole


def seed_rbac_data(db: Session) -> None:
  # 1. Define Basic Permissions
  # Format: {name: description}
  permissions_data = {
    EnumUserPermission.ALL.value: EnumUserPermission.ALL.description,
    EnumUserPermission.USER_CREATE.value: EnumUserPermission.USER_CREATE.description,
    EnumUserPermission.USER_DELETE.value: EnumUserPermission.USER_DELETE.description,
    EnumUserPermission.USER_READ.value: EnumUserPermission.USER_READ.description,
    EnumUserPermission.USER_UPDATE.value: EnumUserPermission.USER_UPDATE.description,
    EnumUserPermission.CONTENT_CREATE.value: EnumUserPermission.CONTENT_CREATE.description,
    EnumUserPermission.CONTENT_READ.value: EnumUserPermission.CONTENT_READ.description,
    EnumUserPermission.CONTENT_UPDATE.value: EnumUserPermission.CONTENT_UPDATE.description,
    EnumUserPermission.CONTENT_PUBLISH.value: EnumUserPermission.CONTENT_PUBLISH.description,
    EnumUserPermission.CONTENT_DELETE.value: EnumUserPermission.CONTENT_DELETE.description,
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
    EnumUserRole.SUPER_ADMIN.value: [EnumUserPermission.ALL.value],
    EnumUserRole.ADMIN.value: [
      EnumUserPermission.USER_CREATE.value,
      EnumUserPermission.USER_DELETE.value,
      EnumUserPermission.USER_READ.value,
      EnumUserPermission.USER_UPDATE.value,
      EnumUserPermission.CONTENT_CREATE.value,
      EnumUserPermission.CONTENT_READ.value,
      EnumUserPermission.CONTENT_UPDATE.value,
      EnumUserPermission.CONTENT_PUBLISH.value,
      EnumUserPermission.CONTENT_DELETE.value,
    ],
    EnumUserRole.EDITOR.value: [
      EnumUserPermission.CONTENT_CREATE.value,
      EnumUserPermission.CONTENT_READ.value,
      EnumUserPermission.CONTENT_UPDATE.value,
    ],
    EnumUserRole.PUBLISHER.value: [
      EnumUserPermission.CONTENT_CREATE.value,
      EnumUserPermission.CONTENT_READ.value,
      EnumUserPermission.CONTENT_UPDATE.value,
      EnumUserPermission.CONTENT_PUBLISH.value,
      EnumUserPermission.CONTENT_DELETE.value,
    ],
    EnumUserRole.USER.value: [
      EnumUserPermission.USER_READ.value,
      EnumUserPermission.CONTENT_READ.value,
    ],
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
    {
      "email": "superadmin@example.com",
      "username": "superadmin",
      "role": EnumUserRole.SUPER_ADMIN.value,
    },
    {"email": "admin@example.com", "username": "admin", "role": EnumUserRole.ADMIN.value},
    {"email": "editor@example.com", "username": "editor", "role": EnumUserRole.EDITOR.value},
    {
      "email": "publisher@example.com",
      "username": "publisher",
      "role": EnumUserRole.PUBLISHER.value,
    },
    {"email": "user@example.com", "username": "user", "role": EnumUserRole.USER.value},
  ]

  hashed_pw = pw_service.password_hash("P@ssw0rd#123")
  for u_data in users_to_create:
    user = db.query(User).filter_by(email=u_data["email"]).first()
    if not user:
      user = User(
        email=u_data["email"],
        password=hashed_pw,
        first_name=u_data["username"].title(),
        last_name="Sample-user",
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
