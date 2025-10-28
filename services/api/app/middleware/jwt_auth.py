"""
Real JWT Authentication Middleware for AutoPro Daune
Replaces mock authentication with REAL Supabase JWT verification
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
import os

security = HTTPBearer()

# Supabase JWT Secret (from env)
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")

class TokenPayload(BaseModel):
    sub: str  # user_id
    email: Optional[str] = None
    role: Optional[str] = "user"
    exp: Optional[int] = None

class CurrentUser(BaseModel):
    id: UUID
    email: Optional[str]
    role: str = "user"

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    Verify JWT token from Supabase
    REAL implementation - no mocks!
    """
    token = credentials.credentials
    
    try:
        # Decode JWT using Supabase secret
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Extract user data
        user_data = TokenPayload(
            sub=payload.get("sub"),
            email=payload.get("email"),
            role=payload.get("role", "user"),
            exp=payload.get("exp")
        )
        
        return user_data
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token_payload: TokenPayload = Depends(verify_token)
) -> CurrentUser:
    """
    Get current authenticated user from token
    """
    try:
        return CurrentUser(
            id=UUID(token_payload.sub),
            email=token_payload.email,
            role=token_payload.role
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

async def get_current_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Verify user has admin role
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user

# Optional auth (allows both authenticated and unauthenticated)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[CurrentUser]:
    """
    Get current user if authenticated, None otherwise
    Useful for endpoints that work differently for auth vs non-auth users
    """
    if not credentials:
        return None
    
    try:
        token_payload = await verify_token(credentials)
        return await get_current_user(token_payload)
    except:
        return None
