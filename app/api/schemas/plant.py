from typing import Optional

from pydantic import BaseModel, Field, model_validator


class BasePlant(BaseModel):
    name: str
    weight: Optional[float] = None
    size: Optional[float] = None
    age: float = Field(ge=0, default=0)
    max_age: float = Field(ge=0, default=0)
    reproduction_age: float = Field(ge=0, default=0)
    fertility_rate: Optional[int] = None
    water_need: Optional[float] = None
    pollinators: Optional[str] = None


class CreatePlant(BasePlant):
    @model_validator(mode="after")
    def validate_ages(self):
        if self.max_age < self.age:
            raise ValueError("Max age needs to be higher than the actual age.")
        if self.reproduction_age > self.max_age:
            raise ValueError("Max age needs to be higher than the reproduction age.")

        return self


class UpdatePlant(BasePlant):
    @model_validator(mode="after")
    def validate_ages(self):
        if self.max_age < self.age:
            raise ValueError("Max age needs to be higher than the actual age.")
        if self.reproduction_age > self.max_age:
            raise ValueError("Max age needs to be higher than the reproduction age.")

        return self


class UpdateEcosystemPlant(BaseModel):
    pollinators: Optional[str] = None
