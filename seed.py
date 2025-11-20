import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from src.utils.db import get_session
from src.v1.model.roles import Role, Permission, PermissionType, PERMISSION_DESCRIPTIONS

async def seed_permissions(session: AsyncSession):
    print("Seeding permissions...")
    existing_permissions = set()
    for p_obj in (await session.execute(sa.select(Permission))).scalars().all():
        existing_permissions.add(p_obj.name)

    permissions_to_add = []
    for perm_name, perm_desc in PERMISSION_DESCRIPTIONS.items():
        if perm_name not in existing_permissions:
            permissions_to_add.append(Permission(name=perm_name, description=perm_desc))
    
    if permissions_to_add:
        session.add_all(permissions_to_add)
        await session.commit()
        print(f"Added {len(permissions_to_add)} new permissions.")
    else:
        print("No new permissions to add.")

async def seed_roles(session: AsyncSession):
    print("Seeding roles...")
    
    # Define roles and their associated permissions
    roles_data = {
        "admin": {
            "description": "Administrator role with full access.",
            "permissions": list(PERMISSION_DESCRIPTIONS.keys()) # All permissions
        },
        "librarian": {
            "description": "Librarian role with resource management permissions.",
            "permissions": [
                PermissionType.CREATE_RESOURCE,
                PermissionType.READ_RESOURCE,
                PermissionType.UPDATE_RESOURCE,
                PermissionType.DELETE_RESOURCE,
                PermissionType.APPROVE_SUBMISSION,
                PermissionType.MANAGE_COLLECTION,
                PermissionType.EDIT_METADATA,
                PermissionType.READ_ROLE # Librarians should be able to read roles
            ]
        },
        "user": {
            "description": "Standard user role with read-only access to resources.",
            "permissions": [
                PermissionType.READ_RESOURCE
            ]
        }
    }

    # Fetch all permissions to establish relationships
    permissions_query = await session.execute(sa.select(Permission))
    all_permissions = {p.name: p for p in permissions_query.scalars().all()}

    for role_name, data in roles_data.items():
        role = await session.execute(Role.__table__.select().where(Role.name == role_name))
        existing_role = role.scalar_one_or_none()

        if not existing_role:
            print(f"Creating role: {role_name}")
            new_role = Role(name=role_name, description=data["description"])
            for perm_name in data["permissions"]:
                if perm_name in all_permissions:
                    new_role.permissions.append(all_permissions[perm_name])
            session.add(new_role)
        else:
            print(f"Role '{role_name}' already exists. Updating permissions...")
            
            # Clear existing permissions and re-add
            existing_role.permissions.clear()
            for perm_name in data["permissions"]:
                if perm_name in all_permissions:
                    existing_role.permissions.append(all_permissions[perm_name])
            session.add(existing_role)
            
    await session.commit()
    print("Roles seeding complete.")


async def main():
    async for session in get_session():
        await seed_permissions(session)
        # await seed_roles(session)
        print("Database seeding complete!")

if __name__ == "__main__":
    asyncio.run(main())
