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
    name: str | None = None
    weight: Optional[float] | None = None
    size: Optional[float] | None = None
    age: float | None = Field(ge=0, default=0)
    max_age: float | None = Field(ge=0, default=0)
    reproduction_age: float | None = Field(ge=0, default=0)
    fertility_rate: Optional[int] | None = None
    water_need: Optional[float] | None = None
    pollinators: Optional[str] | None = None

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


class UpdateEcosystemPlant(BaseModel):
    pollinators: Optional[str] = None
