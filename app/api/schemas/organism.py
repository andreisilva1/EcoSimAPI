from typing import Optional

from pydantic import BaseModel, Field, model_validator


class BaseOrganism(BaseModel):
    name: str
    weight: float
    size: float
    age: float = Field(ge=0, default=0)
    max_age: float = Field(ge=0, default=0)
    reproduction_age: float = Field(ge=0, default=0)
    fertility_rate: int = 1
    water_consumption: float
    food_consumption: float
    predator: Optional[str] = None
    prey: Optional[str] = None
    pollination_target: Optional[str] = None


class CreateOrganism(BaseOrganism):
    @model_validator(mode="after")
    def validate_ages(self):
        if self.max_age < self.age:
            raise ValueError("Max age needs to be higher than the actual age.")
        if self.reproduction_age > self.max_age:
            raise ValueError("Max age needs to be higher than the reproduction age.")

        return self


class UpdateOrganism(BaseOrganism):
    name: str | None = None
    weight: float | None = None
    size: float | None = None
    age: float | None = Field(ge=0, default=None)
    max_age: float | None = Field(ge=0, default=None)
    reproduction_age: float | None = Field(ge=0, default=None)
    fertility_rate: int | None = None
    water_consumption: float | None = None
    food_consumption: float | None = None
    predator: str | None = None
    prey: str | None = None
    pollination_target: str | None = None

    @model_validator(mode="after")
    def validate_ages(self):
        if self.max_age and self.age:
            if self.max_age < self.age:
                raise ValueError("Max age needs to be higher than the actual age.")
            if self.reproduction_age > self.max_age:
                raise ValueError(
                    "Max age needs to be higher than the reproduction age."
                )

        return self


class ReadOrganism(BaseOrganism):
    pass


class UpdateEcosystemOrganism(BaseModel):
    pollination_target: Optional[str] = None
