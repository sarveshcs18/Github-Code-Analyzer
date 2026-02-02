from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.repo import RepoRequest, RepoAnalysisResult
from app.services.github import github_service
from app.services.gemini import gemini_service
from loguru import logger

router = APIRouter()

@router.post("/analyze", response_model=RepoAnalysisResult)
async def analyze_repo(request: RepoRequest):
    """
    Analyze a GitHub repository.
    1. Clone repo (tmp)
    2. Extract structure
    3. Send to Gemini
    4. Return structured summary
    """
    logger.info(f"Received analysis request for: {request.url}")
    try:
        # Step 1: Ingest
        repo_data = await github_service.clone_and_analyze(request.url)
        
        # Step 2: Analyze
        result = await gemini_service.analyze_repo(repo_data)
        
        return result
        
    except ValueError as ie:
        raise HTTPException(status_code=400, detail=str(ie))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
