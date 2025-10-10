"""Pydantic models used by the leads domain."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class LeadAttachment(BaseModel):
    """Metadata for a file attached to a lead."""

    id: Optional[str] = Field(default=None, description="Attachment identifier")
    lead_id: str = Field(..., description="Lead identifier")
    file_name: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="Public URL of the uploaded file")
    storage_key: Optional[str] = Field(default=None, description="Key/path in the storage bucket")
    content_type: Optional[str] = Field(default=None, description="MIME type detected during upload")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    uploaded_by: Optional[str] = Field(default=None, description="User that uploaded the attachment")
    created_at: Optional[datetime] = Field(default=None, description="Timestamp when the attachment was created")


class LeadAttachmentList(BaseModel):
    """Response model for attachment listing."""

    success: bool = True
    lead_id: str
    items: List[LeadAttachment]


class LeadAssignmentRequest(BaseModel):
    """Payload used to assign a lead to someone from the UI."""

    assigned_to: str = Field(..., description="Identifier/name of the assignee")
    assigned_to_email: Optional[EmailStr] = Field(
        default=None, description="Email address used for notification purposes"
    )
    assigned_by: Optional[str] = Field(default=None, description="User performing the assignment")
    notes: Optional[str] = Field(default=None, description="Optional context for the assignment")


class LeadAssignmentResponse(BaseModel):
    """Response returned after a lead assignment."""

    success: bool
    lead_id: str
    assigned_to: str
    assigned_by: Optional[str] = None
    notes: Optional[str] = None


class LeadStatusChange(BaseModel):
    """Represents a status transition in the conversion funnel."""

    id: Optional[str] = None
    lead_id: str
    previous_status: Optional[str] = None
    new_status: str
    changed_by: Optional[str] = None
    notes: Optional[str] = None
    changed_at: Optional[datetime] = None


class LeadStatusHistoryResponse(BaseModel):
    """Response wrapper for status history queries."""

    success: bool = True
    lead_id: str
    items: List[LeadStatusChange]
