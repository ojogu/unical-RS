from typing import List
from src.v1.model import PermissionType


class UtilityService:

    @staticmethod
    def get_valid_permissions() -> List[str]:
        """Utility to get all defined permission string values."""
        # PermissionType.__members__.values() gives us all enum members.
        # We use 'value' to get the string representation (e.g., "create.role").
        return [member.value for member in PermissionType]

    @staticmethod
    def validated_permission(permission_list: List[str]) -> bool:
        """
        Checks if ALL strings in permission_list are valid, existing
        permissions defined in the PermissionType enum.

        Args:
            permission_list: A list of strings representing permissions to check.

        Returns:
            True if all permissions exist in PermissionType, False otherwise.
        """

        # Get the set of all valid permission strings from the enum for fast lookups
        valid_permissions_set = {member.value for member in PermissionType}

        # Check if every item in the input list is present in the set of valid permissions
        for requested_permission in permission_list:
            if requested_permission not in valid_permissions_set:
                return False

        # If the loop completes without returning False, all permissions are valid
        return True