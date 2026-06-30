from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.sharing import ShareRole

class ShareShelfRequest(BaseModel):
    email: EmailStr
    role: ShareRole

class UpdateRoleRequest(BaseModel):
    role: ShareRole

class SharedUserResponse(BaseModel):
    id: int
    email: str
    role: ShareRole

    model_config = ConfigDict(from_attributes=True)
