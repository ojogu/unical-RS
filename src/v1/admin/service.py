from sqlalchemy.ext.asyncio import AsyncSession
from .role_service import RoleService
from .user_management_service import UserManagementService
from .utility_service import UtilityService


class AdminService():
    def __init__(self, db: AsyncSession):
        self.db = db

    def create_admins(self):
        pass


# class SuperAdminService():
#     def __init__(self, db: AsyncSession):
#         self.db = db
#         self.role_service = RoleService(db)
#         self.user_management_service = UserManagementService(db)
#         self.utility_service = UtilityService()

#     # ============ User Operations ============
#     async def fetch_user(self, user_id: str):
#         return await self.user_management_service.fetch_user(user_id)

#     # ============ Role Operations ============
#     async def check_if_roles_exist(self, role_name: str):
#         return await self.role_service.check_if_roles_exist(role_name)

#     async def create_roles(self, role_data):
#         return await self.role_service.create_roles(role_data)

#     async def fetch_one_role(self, role_name: str):
#         return await self.role_service.fetch_one_role(role_name)

#     async def fetch_role_with_permission(self, role_name: str):
#         return await self.role_service.fetch_role_with_permission(role_name)

#     async def fetch_all_roles(self):
#         return await self.role_service.fetch_all_roles()



#     # ============ Admin Operations ============
#     def create_admins(self):
#         pass

#     # ============ Utility Operations ============
#     async def get_user_permissions(self, user_id: str):
#         return await self.user_management_service.get_user_permissions(user_id)

#     @staticmethod
#     def get_valid_permissions():
#         return UtilityService.get_valid_permissions()

#     def validated_permission(self, permission_list):
#         return self.utility_service.validated_permission(permission_list)
