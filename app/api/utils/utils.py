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


def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, set):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, bytes):
        return obj.decode("utf-8")

    else:
        return obj
