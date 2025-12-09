from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Item, ItemSubmission, User
from app.schemas import ItemCreate, ItemOut, ItemSubmissionCreate, ItemSubmissionOut
from datetime import datetime
import os
from typing import List, Optional

router = APIRouter(prefix="/admin/items", tags=["Admin Items"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/submissions")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_admin_key(x_admin_key: Optional[str] = None):
    """Verify admin API key from header"""
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-me")
    if x_admin_key is None or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return True

# ==================== ADMIN ENDPOINTS ====================

@router.get("/", response_model=List[ItemOut])
def list_all_items(db: Session = Depends(get_db)):
    """List all items (public only)"""
    items = db.query(Item).filter(Item.is_public == True).all()
    return items

@router.post("/", response_model=ItemOut)
def create_public_item(
    item: ItemCreate,
    x_admin_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ADMIN ONLY: Add item to general database (visible to all users)
    Requires admin API key header: x-admin-key
    """
    get_admin_key(x_admin_key)
    
    # Check if item already exists
    existing = db.query(Item).filter(Item.name == item.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item '{item.name}' already exists"
        )
    
    new_item = Item(
        name=item.name,
        category=item.category,
        is_public=True,  # Admin-created items are immediately public
        created_by=1  # TODO: Replace with actual admin user ID from token
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/submissions", response_model=List[ItemSubmissionOut])
def list_submissions(
    status_filter: Optional[str] = None,
    x_admin_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ADMIN ONLY: List all user item submissions
    Requires admin API key header: x-admin-key
    
    Query params:
    - status_filter: 'pending', 'approved', 'rejected' (optional)
    """
    get_admin_key(x_admin_key)
    
    query = db.query(ItemSubmission)
    if status_filter:
        query = query.filter(ItemSubmission.status == status_filter)
    
    submissions = query.order_by(ItemSubmission.created_at.desc()).all()
    return submissions

@router.get("/submissions/{item_number}", response_model=ItemSubmissionOut)
def get_submission_by_number(
    item_number: str,
    x_admin_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ADMIN ONLY: Get submission details by item number (e.g., ITEM-001)
    """
    get_admin_key(x_admin_key)
    
    submission = db.query(ItemSubmission).filter(
        ItemSubmission.item_number == item_number
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {item_number} not found"
        )
    
    return submission

@router.patch("/submissions/{item_number}/approve", response_model=ItemSubmissionOut)
def approve_submission(
    item_number: str,
    admin_notes: Optional[str] = None,
    x_admin_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ADMIN ONLY: Approve user submission and create public item
    Also stores the admin notes/feedback
    """
    get_admin_key(x_admin_key)
    
    submission = db.query(ItemSubmission).filter(
        ItemSubmission.item_number == item_number
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {item_number} not found"
        )
    
    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Submission already {submission.status}"
        )
    
    # Create public item from submission
    existing_item = db.query(Item).filter(Item.name == submission.name).first()
    if not existing_item:
        new_item = Item(
            name=submission.name,
            category=submission.category,
            is_public=True,
            created_by=1  # TODO: Replace with actual admin user ID
        )
        db.add(new_item)
        db.flush()
    
    # Update submission status
    submission.status = "approved"
    submission.approved_at = datetime.utcnow()
    submission.approved_by = 1  # TODO: Replace with actual admin user ID
    submission.admin_notes = admin_notes
    
    db.commit()
    db.refresh(submission)
    return submission

@router.patch("/submissions/{item_number}/reject", response_model=ItemSubmissionOut)
def reject_submission(
    item_number: str,
    admin_notes: Optional[str] = None,
    x_admin_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ADMIN ONLY: Reject user submission with feedback
    """
    get_admin_key(x_admin_key)
    
    submission = db.query(ItemSubmission).filter(
        ItemSubmission.item_number == item_number
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {item_number} not found"
        )
    
    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Submission already {submission.status}"
        )
    
    submission.status = "rejected"
    submission.admin_notes = admin_notes or "Rejected by admin"
    
    db.commit()
    db.refresh(submission)
    return submission

# ==================== USER ENDPOINTS ====================

router_user = APIRouter(prefix="/items/submit", tags=["User Items"])

def generate_item_number(db: Session) -> str:
    """Generate unique item number like ITEM-001, ITEM-002, etc."""
    count = db.query(ItemSubmission).count() + 1
    return f"ITEM-{count:03d}"

@router_user.post("/", response_model=ItemSubmissionOut)
async def submit_item(
    name: str = Form(...),
    category: Optional[str] = Form(None),
    price: float = Form(...),
    location: str = Form(...),
    submitter_email: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    USER: Submit new item for admin approval
    
    Fields:
    - name: Item name (required)
    - category: Category (optional)
    - price: Current price (required)
    - location: Location name (required) - use location picker result
    - submitter_email: Your email (optional)
    - image: Proof/screenshot (optional, multipart/form-data)
    
    Returns: submission with auto-generated item number (e.g., ITEM-001)
    """
    
    # Validate price
    if price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )
    
    # Generate unique item number
    item_number = generate_item_number(db)
    
    # Create submission folder
    submission_folder = os.path.join(UPLOAD_DIR, item_number)
    os.makedirs(submission_folder, exist_ok=True)
    
    image_path = None
    if image:
        # Save uploaded image
        file_path = os.path.join(submission_folder, image.filename)
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            image_path = file_path
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image: {str(e)}"
            )
    
    # Create submission record
    submission = ItemSubmission(
        item_number=item_number,
        name=name,
        category=category,
        price=price,
        location=location,
        submitter_id=1,  # TODO: Replace with actual user ID from token
        submission_folder=submission_folder,
        image_path=image_path,
        status="pending"
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return submission

@router_user.get("/{item_number}")
def get_submission_status(
    item_number: str,
    db: Session = Depends(get_db)
):
    """
    USER: Check status of your submission by item number
    """
    submission = db.query(ItemSubmission).filter(
        ItemSubmission.item_number == item_number
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {item_number} not found"
        )
    
    return {
        "item_number": submission.item_number,
        "name": submission.name,
        "status": submission.status,
        "created_at": submission.created_at,
        "approved_at": submission.approved_at,
        "admin_notes": submission.admin_notes
    }
