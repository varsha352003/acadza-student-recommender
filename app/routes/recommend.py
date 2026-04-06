from fastapi import APIRouter, HTTPException

from app.services.recommender import StudentRecommender


router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.post("/{student_id}")
async def recommend(student_id: str):
    """
    Generate personalized learning recommendations for a student.
    """
    recommender = StudentRecommender()
    result = recommender.generate_recommendation(student_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return result
