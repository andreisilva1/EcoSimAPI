from fastapi import HTTPException, status


class RESOURCE_ID_NOT_FOUND_ERROR(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {resource_name} found with the provided ID.",
        )


class RESOURCE_NAME_ALREADY_EXISTS_ERROR(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"A {resource_name} with this name already exists.",
        )


class RESOURCE_NAME_NOT_FOUND_ERROR(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {resource_name} found with the provided name.",
        )


class RESOURCE_NAME_OR_ID_NOT_FOUND_ERROR(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {resource_name} found with the provided name or ID.",
        )


class BLANK_UPDATE_FIELDS_ERROR(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No update fields has been filled.",
        )


class RESOURCE_NOT_FOUND_IN_RELATIONSHIP_ERROR(HTTPException):
    def __init__(self, one: str, many: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The provided {many} doesn't exist in the {one}.",
        )


class POLLINATORS_NOT_FOUND_ERROR(HTTPException):
    def __init__(self, pollinator_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No organism with that name was found: ({pollinator_name}). You can delete it from the pollinators field or correct its name.",
        )


class ALL_DEFAULTS_ALREADY_EXISTS_ERROR(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All the default {resource_name} already exists",
        )


class ECOSYSTEM_ALREADY_IN_SIMULATION_ERROR(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The ecosystem {resource_name} is already in simulation.",
        )


class SIMULATION_NOT_EXISTS_ERROR(HTTPException):
    def __init__(self, resource_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation not found with that ID.",
        )
