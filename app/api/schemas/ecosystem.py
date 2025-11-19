from pydantic import BaseModel, Field, model_validator


class BaseEcoSystem(BaseModel):
    name: str
    water_available: float
    minimum_water_to_add_per_simulation: int = Field(ge=0, default=0)
    max_water_to_add_per_simulation: int = Field(ge=0, default=0)

    @model_validator(mode="after")
    def validate_ages(self):
        if (
            self.minimum_water_to_add_per_simulation
            and self.max_water_to_add_per_simulation
        ):
            if (
                self.minimum_water_to_add_per_simulation
                > self.max_water_to_add_per_simulation
            ):
                raise ValueError(
                    "Max water to add per simulation should be higher than the minimum water to add per simulation."
                )

        return self


class CreateEcoSystem(BaseEcoSystem):
    pass


class UpdateEcoSystem(BaseEcoSystem):
    pass
