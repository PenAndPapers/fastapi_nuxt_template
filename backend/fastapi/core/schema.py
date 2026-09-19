# ----------------------------------------------------------
#  Contains reusable schemas for common data types
# ----------------------------------------------------------


from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import AfterValidator, BaseModel, Field, StringConstraints

from utils.password import is_valid_password

# ----------------------------------------------------------
#  Custom string types
# ----------------------------------------------------------

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
ValidPassword = Annotated[str, AfterValidator(is_valid_password)]


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
