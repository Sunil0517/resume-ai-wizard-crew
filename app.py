"""
FastAPI application for the AI Resume Checker using Crew AI agents.
"""

import os
import uvicorn
import tempfile
import json
import uuid
from typing import Dict, Optional, List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from crewai import Crew
from agents.resume_parser import ResumeParser
from agents.resume_scorer import ResumeScorer
from agents.resume_improver import ResumeImprover

# Define response models
class JobRequirement(BaseModel):
    id: str
    title: str
    required_skills: List[str]
    min_years_experience: int
    min_education: str
    description: Optional[str] = None
    
class CustomJobRequirement(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    min_years_experience: int 
    min_education: str

class CreateUserJobRequest(BaseModel):
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Detailed job description")
    required_skills: List[str] = Field(..., description="List of required skills")
    min_years_experience: int = Field(0, description="Minimum years of experience required")
    min_education: str = Field("Bachelor's degree", description="Minimum education level required")
    
class UserJobResponse(BaseModel):
    id: str
    title: str
    description: str
    required_skills: List[str]
    min_years_experience: int
    min_education: str
    created_at: str
    
class ResumeScore(BaseModel):
    overall_score: float
    skill_match_score: float
    experience_score: float
    education_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    analysis: Optional[str] = None

class ResumeCheckResult(BaseModel):
    parsed_resume: Dict
    job_data: JobRequirement
    score: ResumeScore
    feedback: str
    improved_resume: str

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Checker API",
    description="API for analyzing and improving resumes using AI agents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock job data for demo purposes (replace with actual API calls in production)
mock_jobs = {
    "job1": {
        "id": "job1",
        "title": "Senior Software Engineer",
        "required_skills": ["python", "javascript", "react", "aws", "docker", "kubernetes"],
        "min_years_experience": 5,
        "min_education": "Bachelor's degree"
    },
    "job2": {
        "id": "job2",
        "title": "Data Scientist",
        "required_skills": ["python", "sql", "machine learning", "pandas", "pytorch", "statistics"],
        "min_years_experience": 3,
        "min_education": "Master's degree"
    },
    "job3": {
        "id": "job3",
        "title": "Product Manager",
        "required_skills": ["agile", "jira", "user stories", "roadmap planning", "stakeholder management"],
        "min_years_experience": 4,
        "min_education": "Bachelor's degree"
    }
}

# In-memory storage for user-created job roles (in production, use a database)
user_jobs = {}

# Initialize agents
resume_parser = ResumeParser()
resume_scorer = ResumeScorer()
resume_improver = ResumeImprover()

# Serve static files from the frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_root():
    """API root endpoint."""
    return {"message": "Welcome to the AI Resume Checker API", "version": "1.0.0"}

@app.get("/api/jobs")
async def list_jobs():
    """List all available jobs."""
    return list(mock_jobs.values())

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details by ID."""
    if job_id not in mock_jobs:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
    
    return mock_jobs[job_id]

# User job roles management endpoints
@app.post("/api/user-jobs", response_model=UserJobResponse, status_code=201)
async def create_user_job(job: CreateUserJobRequest):
    """Create a new user-defined job role."""
    job_id = str(uuid.uuid4())
    timestamp = import_datetime_now()
    
    user_jobs[job_id] = {
        "id": job_id,
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills,
        "min_years_experience": job.min_years_experience,
        "min_education": job.min_education,
        "created_at": timestamp.isoformat()
    }
    
    return user_jobs[job_id]

@app.get("/api/user-jobs", response_model=List[UserJobResponse])
async def list_user_jobs():
    """List all user-defined job roles."""
    return list(user_jobs.values())

@app.get("/api/user-jobs/{job_id}", response_model=UserJobResponse)
async def get_user_job(job_id: str):
    """Get a specific user-defined job role."""
    if job_id not in user_jobs:
        raise HTTPException(status_code=404, detail=f"User job ID {job_id} not found")
    
    return user_jobs[job_id]

@app.put("/api/user-jobs/{job_id}", response_model=UserJobResponse)
async def update_user_job(job_id: str, job: CreateUserJobRequest):
    """Update a user-defined job role."""
    if job_id not in user_jobs:
        raise HTTPException(status_code=404, detail=f"User job ID {job_id} not found")
    
    user_jobs[job_id].update({
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills,
        "min_years_experience": job.min_years_experience,
        "min_education": job.min_education
    })
    
    return user_jobs[job_id]

@app.delete("/api/user-jobs/{job_id}", status_code=204)
async def delete_user_job(job_id: str):
    """Delete a user-defined job role."""
    if job_id not in user_jobs:
        raise HTTPException(status_code=404, detail=f"User job ID {job_id} not found")
    
    del user_jobs[job_id]
    return None

@app.post("/api/check-resume")
async def check_resume(
    resume: UploadFile = File(...),
    job_id: str = Form(...)
):
    """
    Upload and analyze a resume against a specific job.
    
    Args:
        resume: Resume file (PDF or DOCX)
        job_id: Job ID to compare against
    
    Returns:
        Analysis results including parsed resume, scores, feedback, and improved resume
    """
    # Check if this is a predefined job or user job
    if job_id in mock_jobs:
        job_data = mock_jobs[job_id]
    elif job_id in user_jobs:
        job_data = user_jobs[job_id]
    else:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
    
    # Save uploaded file to temp location
    try:
        # Create temp file with correct extension
        suffix = os.path.splitext(resume.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            contents = await resume.read()
            temp_file.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    try:
        # Set up CrewAI crew
        crew = Crew(
            agents=[
                resume_parser.create_crew_agent(),
                resume_scorer.create_crew_agent(),
                resume_improver.create_crew_agent()
            ],
            tasks=[
                *resume_parser.define_tasks(),
                *resume_scorer.define_tasks(),
                *resume_improver.define_tasks()
            ],
            verbose=True
        )
        
        # Parse resume
        resume_data = resume_parser.load_resume(temp_path)
        resume_text = resume_parser.extract_text(resume_data)
        parsed_resume = resume_parser.parse_entities(resume_text)
        
        # Compute score
        score_data = resume_scorer.compute_score(parsed_resume, job_data)
        
        # Generate feedback and improved resume
        feedback = resume_improver.generate_feedback(parsed_resume, score_data)
        improved_resume = resume_improver.rewrite_resume(parsed_resume, score_data, feedback)
        
        # Return the results
        return ResumeCheckResult(
            parsed_resume=parsed_resume,
            job_data=job_data,
            score=score_data,
            feedback=feedback,
            improved_resume=improved_resume
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.post("/api/check-resume-with-custom-job")
async def check_resume_with_custom_job(
    resume: UploadFile = File(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    required_skills: str = Form(...),  # Comma-separated list
    min_years_experience: int = Form(0),
    min_education: str = Form("Bachelor's degree")
):
    """
    Upload and analyze a resume against a custom job description.
    
    Args:
        resume: Resume file (PDF or DOCX)
        job_title: Title of the job
        job_description: Detailed job description
        required_skills: Comma-separated list of required skills
        min_years_experience: Minimum years of experience required
        min_education: Minimum education level required
    
    Returns:
        Analysis results including parsed resume, scores, feedback, and improved resume
    """
    # Save uploaded file to temp location
    try:
        # Create temp file with correct extension
        suffix = os.path.splitext(resume.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            contents = await resume.read()
            temp_file.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    try:
        # Parse skills from comma-separated string
        skills_list = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
        
        # Create custom job data
        job_data = {
            "id": "custom",
            "title": job_title,
            "description": job_description,
            "required_skills": skills_list,
            "min_years_experience": min_years_experience,
            "min_education": min_education
        }
        
        # Set up CrewAI crew
        crew = Crew(
            agents=[
                resume_parser.create_crew_agent(),
                resume_scorer.create_crew_agent(),
                resume_improver.create_crew_agent()
            ],
            tasks=[
                *resume_parser.define_tasks(),
                *resume_scorer.define_tasks(),
                *resume_improver.define_tasks()
            ],
            verbose=True
        )
        
        # Parse resume
        resume_data = resume_parser.load_resume(temp_path)
        resume_text = resume_parser.extract_text(resume_data)
        parsed_resume = resume_parser.parse_entities(resume_text)
        
        # Compute score
        score_data = resume_scorer.compute_score(parsed_resume, job_data)
        
        # Generate feedback and improved resume
        feedback = resume_improver.generate_feedback(parsed_resume, score_data)
        improved_resume = resume_improver.rewrite_resume(parsed_resume, score_data, feedback)
        
        # Return the results
        return ResumeCheckResult(
            parsed_resume=parsed_resume,
            job_data=job_data,
            score=score_data,
            feedback=feedback,
            improved_resume=improved_resume
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def import_datetime_now():
    """Import datetime and return current time."""
    from datetime import datetime
    return datetime.now()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
