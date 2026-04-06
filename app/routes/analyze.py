from fastapi import APIRouter, HTTPException

from app.services.analyzer import analyze_student


router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/{student_id}")
async def analyze(student_id: str):
    """
    Analyze student performance and return metrics.
    """
    result = analyze_student(student_id)
    
    if not result or result['total_attempts'] == 0:
        raise HTTPException(status_code=404, detail="Student not found or has no attempts")
    
    return result
