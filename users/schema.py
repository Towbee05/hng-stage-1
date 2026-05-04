from ninja import Schema

class TokenRefreshInputSchema(Schema):
    refresh_token: str

class TokenPairOutputSchema(Schema):
    access_token: str
    refresh_token: str

class TokenPairOutputResponseSchema(Schema):
    status: str
    data: TokenPairOutputSchema

class UserSchema(Schema):
    id: str
    github_id: str
    username: str
    email: str
    avatar_url: str
    role: str
    is_staff: bool
    is_superuser: bool
    is_active: bool
    created_at: bool
    
class PassToClientSchema(Schema):
    authentication_url: str
    state: str
