"""Bulk operations for importing members via CSV/Excel."""

import csv
import io
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.member import MemberStatus
from app.models.user import User, UserRole
from app.schemas.member import MemberCreate
from app.services import member_service
from app.utils import responses
from app.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter()

ADMIN_ROLES = (UserRole.SUPER_ADMIN, UserRole.ADMIN)


class BulkImportResult(BaseModel):
    """Result of bulk import operation."""
    imported: int
    errors: int
    skipped: int
    members: List[dict]
    errorDetails: List[dict]


@router.post("/members/import", response_model=BulkImportResult)
async def import_members_csv(
    file: UploadFile = File(..., description="CSV file with member data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*ADMIN_ROLES)),
):
    """
    Import members from CSV file.

    Required columns:
    - firstName
    - lastName



@router.post("/members/import")
async def import_members_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*ADMIN_ROLES)),
):
    """
    Import members from CSV file.

    CSV Format:
    firstName, lastName, email, phoneNumber, whatsAppNumber, weChatID, country, school, gender, tags, notes

    Required columns:
    - firstName(can include middle names, e.g., "Enoch Kwateh")
    - lastName(e.g., "Dongbo")

    Optional columns:
    - email
    - phoneNumber
    - whatsAppNumber
    - weChatID
    - country
    - school
    - gender(Male/Female)
    - tags(comma-separated: music, choir, youth)
    - notes
    """
    if not file.filename or not file.filename.endswith('.csv'):
        raise ValidationError({"file": "Only CSV files are supported"})

    try:
        # Read file content
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))

        imported = []
        errors = []
        skipped = 0

        # Start at 2 (header is row 1)
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Skip empty rows
                if not row.get('firstName', '').strip():
                    skipped += 1
                    continue

                # Parse tags
                tags_str = row.get('tags', '').strip()
                tags = [tag.strip() for tag in tags_str.split(
                    ',') if tag.strip()] if tags_str else []

                # Parse gender
                gender = row.get('gender', '').strip()
                if gender and gender not in ['Male', 'Female']:
                    gender = None

                # Create member payload
                member_data = MemberCreate(
                    firstName=row['firstName'].strip(),
                    lastName=row.get('lastName', '').strip() or None,
                    email=row.get('email', '').strip() or None,
                    phoneNumber=row.get('phoneNumber', '').strip() or None,
                    whatsAppNumber=row.get(
                        'whatsAppNumber', '').strip() or None,
                    weChatID=row.get('weChatID', '').strip() or None,
                    tags=tags,
                    customFields={
                        'country': row.get('country', '').strip() or None,
                        'school': row.get('school', '').strip() or None,
                        'gender': gender,
                        'notes': row.get('notes', '').strip() or None,
                    },
                    memberStatus=MemberStatus.ACTIVE,
                )

                # Create member
                member = member_service.create_member(
                    db, member_data, current_user=current_user)
                imported.append({
                    'id': member.id,
                    'name': f"{member.first_name} {member.last_name or ''}".strip(),
                    'email': member.email,
                })

            except Exception as e:
                logger.error(f"Error importing row {row_num}: {e}")
                errors.append({
                    'row': row_num,
                    'data': dict(row),
                    'error': str(e)
                })

        result = BulkImportResult(
            imported=len(imported),
            errors=len(errors),
            skipped=skipped,
            members=imported,
            errorDetails=errors[:10],  # Return first 10 errors
        )

        return responses.success_response(result.model_dump(), status_code=status.HTTP_201_CREATED)

    except UnicodeDecodeError:
        raise ValidationError({"file": "File must be UTF-8 encoded"})
    except Exception as e:
        logger.error(f"CSV import failed: {e}")
        raise ValidationError({"file": f"Failed to process CSV: {str(e)}"})


@router.get("/members/import-template")
async def download_import_template(
    _: User = Depends(deps.get_current_user)
):
    """Download CSV template for member import ."""
    from fastapi.responses import StreamingResponse

    template = """firstName, lastName, email, phoneNumber, whatsAppNumber, weChatID, country, school, gender, tags, notes
John, Doe, john.doe@example.com, 1234567890, 1234567890, johndoe123, USA, University of Example, Male, "choir,youth", Regular attendee
Jane, Smith, jane.smith@example.com, 0987654321, 0987654321, janesmith456, Canada, Example College, Female, music, New member
Enoch Kwateh, Dongbo, ekd@ekddigital.com, 8618506832159, 8618506832159, EKD231777285010, Liberia, University of Jinan, Male, "management,prayer,music", Service Management Team
"""
    
    return StreamingResponse(
        io.StringIO(template),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=members_import_template.csv"
        }
    )
