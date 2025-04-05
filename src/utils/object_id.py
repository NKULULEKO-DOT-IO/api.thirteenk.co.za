from bson import ObjectId
from bson.errors import InvalidId


def is_valid_object_id(id_str: str) -> bool:
    """
    Check if a string is a valid MongoDB ObjectId.

    Args:
        id_str: String to check

    Returns:
        True if valid, False otherwise
    """
    try:
        ObjectId(id_str)
        return True
    except (InvalidId, TypeError):
        return False