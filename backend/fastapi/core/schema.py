# ----------------------------------------------------------
#  Contains reusable schemas for common data types
# ----------------------------------------------------------


from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

# ----------------------------------------------------------
#  Custom string types
# ----------------------------------------------------------

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


# ----------------------------------------------------------
#  Custom Integer types
# ----------------------------------------------------------

PositiveInt = Annotated[int, Field(ge=1)]
NegativeInt = Annotated[int, Field(le=-1)]


# ----------------------------------------------------------
#  Custom Response types
# ----------------------------------------------------------
class GenericResponseMessage(BaseModel):
  message: str = Field(
    ...,
    description="Response message.",
    json_schema_extra={"example": "Operation completed successfully."},
  )
