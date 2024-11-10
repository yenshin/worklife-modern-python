from pydantic import BaseModel, ConfigDict
import uuid


class BaseRepresentation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
