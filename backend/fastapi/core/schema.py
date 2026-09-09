# ----------------------------------------------------------
#  Contains reusable schemas for common data types
# ----------------------------------------------------------


from typing import Annotated

from pydantic import Field, StringConstraints

# ---- String schemas ----

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


# ---- Integer schemas ----

PositiveInt = Annotated[int, Field(min=1)]
NegativeInt = Annotated[int, Field(max=-1)]
