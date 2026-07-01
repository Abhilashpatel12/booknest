from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.sharing import ShareRole

class ShareShelfRequest(BaseModel):
    email: EmailStr
    role: ShareRole

class UpdateRoleRequest(BaseModel):
    role: ShareRole

class UserBasicResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)

class SharedUserResponse(BaseModel):
    id: int
    user: UserBasicResponse
    role: ShareRole

    model_config = ConfigDict(from_attributes=True)
