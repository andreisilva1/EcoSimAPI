from fastapi import HTTPException, status


class RESOURCE_ID_NOT_FOUND(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {resource_name} found with the provided ID.",
        )


class RESOURCE_NAME_ALREADY_EXISTS(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"A {resource_name} with this name already exists.",
        )


class RESOURCE_NAME_NOT_FOUND(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {resource_name} found with the provided name.",
        )


class RESOURCE_NAME_OR_ID_NOT_FOUND(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {resource_name} found with the provided name or ID.",
        )


class BLANK_UPDATE_FIELDS(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No update fields has been filled.",
        )


class RESOURCE_NOT_FOUND_IN_RELATIONSHIP(HTTPException):
    def __init__(self, one: str, many: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The provided {many} doesn't exist in the {one}.",
        )


class POLLINATORS_NOT_FOUND(HTTPException):
    def __init__(self, pollinator_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No organism with that name was found: ({pollinator_name}). You can delete it from the pollinators field or correct its name.",
        )
