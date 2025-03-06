"""
API Service for Outlier Detection and Rule Integration.

This module provides a FastAPI application with endpoints for:
- Registering outlier detection tasks
- Retrieving outlier detection results
- Integrating expert rules with machine learning models
"""

from fastapi import FastAPI, HTTPException, Depends, Path, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from enum import Enum
import redis
import uuid
import logging
import json
import traceback
from typing import List, Optional, Dict, Any, Union

from utils.tasks import outlier_detection_from_data, extract_and_integrate_expert_rules
from utils.redis import redis_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define constants
REDIS_TASK_DATA_DB = 1
REDIS_OUTLIER_RESULTS_DB = 2
REDIS_INTEGRATED_RESULTS_DB = 4


class OutlierDetectionAlgorithm(str, Enum):
    """Supported algorithms for outlier detection."""
    LocalOutlierFactor = "LocalOutlierFactor"
    IsolationForest = "IsolationForest"
    OneClassSVM = "OneClassSVM"


class RulesAlgorithm(str, Enum):
    """Supported algorithms for rules generation."""
    FIGS = "FIGS"
    OptimalTree = "OptimalTree"
    GreedyTree = "GreedyTree"


class RegisterTaskRequest(BaseModel):
    """Request model for registering a new outlier detection task."""
    data_algorithm: OutlierDetectionAlgorithm = Field(
        ..., 
        description="Algorithm to use for outlier detection"
    )
    rules_algorithm: RulesAlgorithm = Field(
        ..., 
        description="Algorithm to use for rules generation"
    )
    expert_text: str = Field(
        ..., 
        description="Expert knowledge text to integrate with the rules"
    )
    # Changed from Dict[str, List[Any]] back to dict for backward compatibility
    json_dict: dict = Field(
        ..., 
        description="Dataset as a dictionary with column names as keys and lists of values"
    )

    class Config:
        schema_extra = {
            "example": {
                "data_algorithm": "IsolationForest",
                "rules_algorithm": "FIGS",
                "expert_text": "If temperature > 30 and humidity < 20, this is an outlier.",
                "json_dict": {
                    "temperature": [20, 25, 30, 35],
                    "humidity": [40, 35, 25, 15]
                }
            }
        }


class RegisteredTaskResponse(BaseModel):
    """Response model for task registration."""
    task_id: str = Field(..., description="Unique ID for the registered task")
    status: str = Field(..., description="Status of the task registration")


class ImageResponse(BaseModel):
    """Response model for image data."""
    image_url: str = Field(
        ..., 
        description="Base64 encoded image URL or empty string if no image is available"
    )


class RuleListResponse(BaseModel):
    """Response model for rule lists."""
    rules: List[str] = Field(
        ..., 
        description="List of rules extracted from the models"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error description")


# Initialize FastAPI app with metadata
app = FastAPI(
    title="Outlier Detection & Rule Integration API",
    description="API for outlier detection and expert rule integration for agentic systems",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_task_data(
    task_id: str = Path(..., description="Unique task identifier"),
    db: int = REDIS_OUTLIER_RESULTS_DB,
    skip_check: bool = False
) -> Dict[str, Any]:
    """
    Retrieve task data from Redis.
    
    Args:
        task_id: The unique identifier for the task
        db: The Redis database to retrieve from
        skip_check: Whether to skip the task status check
        
    Returns:
        The task data dictionary
        
    Raises:
        HTTPException: If task is not found or not completed
    """
    try:
        with redis_connection(db=db) as r:
            task_data = r.get(task_id)
            if not task_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Task not found or task not finished yet"
                )
            task = json.loads(task_data)
    except redis.exceptions.RedisError as exc:
        logger.error(f"Redis error for task {task_id}: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task data from database"
        )
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON data for task {task_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid task data format"
        )
    
    if not skip_check and task.get('status') != 'success':
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED, 
            detail="Task is still processing"
        )
    
    return task


@app.post(
    "/register_data/", 
    response_model=RegisteredTaskResponse, 
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Register a new outlier detection task",
    description="Register a dataset and expert knowledge for outlier detection and rule integration"
)
async def register_data(request: RegisterTaskRequest) -> RegisteredTaskResponse:
    """
    Register data for outlier detection and rule integration.
    
    This endpoint starts an asynchronous process that:
    1. Performs outlier detection using the specified algorithm
    2. Integrates expert rules with the detection results
    
    Returns a task ID that can be used to retrieve results later.
    """
    task_id = str(uuid.uuid4())
    logger.info(f"Registering new task {task_id} with {request.data_algorithm} and {request.rules_algorithm}")
    
    try:
        with redis_connection(db=REDIS_TASK_DATA_DB) as r:
            r.set(task_id, request.model_dump_json())
    except redis.exceptions.RedisError:
        logger.error(f"Redis error during task registration: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to store task data"
        )

    try:
        # Start processing in background (in a real production system, 
        # this would use a task queue like Celery)
        outlier_detection_from_data(task_id)
        extract_and_integrate_expert_rules(task_id)
    except Exception:
        logger.error(f"Error starting task processing: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Task processing could not be initiated"
        )

    return RegisteredTaskResponse(task_id=task_id, status="success")


@app.get(
    "/tasks/{task_id}/outliers_from_data_img", 
    response_model=ImageResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        202: {"model": ErrorResponse}
    },
    summary="Get visualization of outlier detection results",
    description="Retrieve the decision tree visualization from the outlier detection process"
)
async def get_outliers_from_data_image(
    task_data: Dict[str, Any] = Depends(get_task_data)
) -> ImageResponse:
    """Get the visualization image for outlier detection results."""
    return ImageResponse(image_url=task_data.get('image_url', ''))


@app.get(
    "/tasks/{task_id}/outliers_from_data", 
    response_model=RuleListResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        202: {"model": ErrorResponse}
    },
    summary="Get rules from outlier detection",
    description="Retrieve the rules extracted from the outlier detection model"
)
async def get_outliers_from_data_rules(
    task_data: Dict[str, Any] = Depends(get_task_data)
) -> RuleListResponse:
    """Get the rules extracted from outlier detection."""
    return RuleListResponse(rules=task_data.get('rules', []))


@app.get(
    "/tasks/{task_id}/outliers_integrated_img", 
    response_model=ImageResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        202: {"model": ErrorResponse}
    },
    summary="Get visualization of integrated rules",
    description="Retrieve the decision tree visualization after expert rule integration"
)
async def get_outliers_integrated_image(
    task_id: str = Path(..., description="Unique task identifier")
) -> ImageResponse:
    """Get the visualization image for integrated outlier rules."""
    task_data = await get_task_data(task_id=task_id, db=REDIS_INTEGRATED_RESULTS_DB)
    return ImageResponse(image_url=task_data.get('image_url', ''))


@app.get(
    "/tasks/{task_id}/outliers_integrated", 
    response_model=RuleListResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get integrated outlier rules",
    description="Retrieve the rules after integrating expert knowledge with outlier detection"
)
async def get_outliers_integrated_rules(
    task_id: str = Path(..., description="Unique task identifier")
) -> RuleListResponse:
    """Get the integrated rules from expert knowledge and outlier detection."""
    task_data = await get_task_data(
        task_id=task_id, 
        db=REDIS_INTEGRATED_RESULTS_DB, 
        skip_check=True
    )
    return RuleListResponse(rules=task_data.get('rules_integrated', []))


@app.get(
    "/tasks/{task_id}/outliers_new_rules", 
    response_model=RuleListResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get new rules from integrated model",
    description="Retrieve the new rules extracted from the model after integration"
)
async def get_outliers_new_rules(
    task_id: str = Path(..., description="Unique task identifier")
) -> RuleListResponse:
    """Get the new rules extracted from the integrated model."""
    task_data = await get_task_data(
        task_id=task_id, 
        db=REDIS_INTEGRATED_RESULTS_DB, 
        skip_check=True
    )
    return RuleListResponse(rules=task_data.get('new_rules', []))


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Handle unexpected exceptions and return a clean error response."""
    logger.error(f"Unhandled exception: {traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
