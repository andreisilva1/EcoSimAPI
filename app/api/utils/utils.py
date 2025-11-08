from uuid import UUID

from fastapi import HTTPException, status


def verify_uuid(string_id: str):
    try:
        return UUID(string_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a real UUID.",
        )
