"""
FastAPI application for the AI Resume Checker using Crew AI agents.

This application provides an API for analyzing resumes against job requirements and
generating personalized feedback and improvements using AI.
"""

import os
import uvicorn
import tempfile
import json
import uuid
import traceback
from typing import Dict, Optional, List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel, Field

from crewai import Crew
from agents.resume_parser import ResumeParser
from agents.resume_scorer import ResumeScorer
from agents.resume_improver import ResumeImprover

# Define response models
class ResumeScore(BaseModel):
    """Model for resume scoring results."""
    overall_score: float
    skill_match_score: float
    experience_score: float
    education_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    analysis: Optional[str] = None

class JobRequirement(BaseModel):
    """Model for job requirements."""
    id: str
    title: str
    required_skills: List[str]
    min_years_experience: int
    min_education: str
    description: Optional[str] = None

class ResumeCheckResult(BaseModel):
    """Model for resume analysis results."""
    parsed_resume: Dict
    job_data: JobRequirement
    score: ResumeScore
    feedback: str
    improved_resume: str

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Checker API",
    description="API for analyzing and improving resumes against job requirements using AI agents",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agents
resume_parser = ResumeParser()
resume_scorer = ResumeScorer()
resume_improver = ResumeImprover()

# Custom exception handler to return proper JSON responses
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions and return proper JSON error responses."""
    error_detail = str(exc)
    error_traceback = traceback.format_exc()
    
    # Log the full error for debugging
    print(f"Error processing request: {error_detail}")
    print(f"Traceback: {error_traceback}")
    
    # Return a clean JSON response
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {error_detail}"}
    )

# Serve static files from project directories
# Check which directories exist and use the appropriate one
for frontend_dir in ["frontend", "dist", "src"]:
    if os.path.exists(frontend_dir):
        print(f"Found frontend directory: {frontend_dir}")
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
        break
else:
    print("Warning: No frontend directory found. Static files will not be served.")

# Try to serve assets if the directory exists
if os.path.exists("public"):
    app.mount("/assets", StaticFiles(directory="public"), name="assets")
else:
    print("Warning: Public assets directory not found.")

# Serve the frontend HTML file
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend React application."""
    # Look for index.html in different possible locations
    for path in ["frontend/index.html", "dist/index.html", "index.html"]:
        if os.path.exists(path):
            return FileResponse(path)
    
    # If no index.html is found, return a basic HTML response
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
        <head>
            <title>AI Resume Checker</title>
        </head>
        <body>
            <h1>AI Resume Checker API</h1>
            <p>Frontend not found. Please build the frontend with <code>npm run build</code> or run <code>python setup.py</code>.</p>
        </body>
    </html>
    """, status_code=200)

@app.get("/api")
async def read_api_root():
    """API root endpoint with information about the API."""
    return {
        "message": "Welcome to the AI Resume Checker API", 
        "version": "1.0.0",
        "endpoints": {
            "Resume Analysis": "/api/analyze-resume-with-requirements",
            "Documentation": "/api/docs"
        }
    }

@app.post("/api/analyze-resume-with-requirements", response_model=ResumeCheckResult)
async def analyze_resume_with_requirements(
    resume: UploadFile = File(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    required_skills: str = Form(...),  # Comma-separated list
    min_years_experience: int = Form(0),
    min_education: str = Form("Bachelor's degree")
):
    """
    Analyze a resume against custom job requirements.
    
    This endpoint accepts a resume file and job requirements, then:
    1. Parses the resume using AI to extract structured information
    2. Scores the resume against the provided job requirements
    3. Generates personalized feedback on improving the resume
    4. Creates an optimized version of the resume tailored to the job
    
    Args:
        resume: Resume file (PDF or DOCX)
        job_title: Title of the job
        job_description: Job description
        required_skills: Comma-separated list of required skills
        min_years_experience: Minimum years of experience
        min_education: Minimum education level
    
    Returns:
        Analysis results including parsed resume, scores, feedback, and improved resume
    """
    # Validate resume file
    if not resume.filename:
        raise HTTPException(status_code=400, detail="Resume file is missing")
    
    # Check file extension
    file_ext = os.path.splitext(resume.filename)[1].lower()
    if file_ext not in ['.pdf', '.docx']:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format: {file_ext}. Only PDF and DOCX files are supported."
        )
    
    # Check file size (limit to 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    contents = await resume.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds the 10MB limit. Please upload a smaller file."
        )
    
    # Reset file stream position
    await resume.seek(0)
    
    # Validate job requirements
    if not job_title or not job_title.strip():
        raise HTTPException(status_code=400, detail="Job title is required")
    
    if not required_skills or not required_skills.strip():
        raise HTTPException(status_code=400, detail="Required skills are required")
    
    # Create a temporary file
    temp_path = None
    try:
        # Create temp file with correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_path = temp_file.name
            temp_file.write(contents)
            
        # Parse skills from comma-separated string
        skills_list = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
        
        if not skills_list:
            raise HTTPException(status_code=400, detail="At least one valid skill is required")
        
        # Create job data for processing
        job_data = {
            "id": "direct",
            "title": job_title,
            "description": job_description,
            "required_skills": skills_list,
            "min_years_experience": min_years_experience,
            "min_education": min_education
        }
        
        # Parse resume
        try:
            resume_data = resume_parser.load_resume(temp_path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid resume format: {str(e)}")
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Error processing uploaded file")
        
        try:
            resume_text = resume_parser.extract_text(resume_data)
            parsed_resume = resume_parser.parse_entities(resume_text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Resume validation failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing resume content: {str(e)}")
        
        # Compute score
        try:
            score_data = resume_scorer.compute_score(parsed_resume, job_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Error calculating resume score: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in resume scoring: {str(e)}")
        
        # Generate feedback and improved resume
        try:
            feedback = resume_improver.generate_feedback(parsed_resume, score_data)
            improved_resume = resume_improver.rewrite_resume(parsed_resume, score_data, feedback)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating feedback and improvements: {str(e)}")
        
        # Create properly formatted result object
        result = ResumeCheckResult(
            parsed_resume=parsed_resume,
            job_data=JobRequirement(
                id="direct",
                title=job_title,
                description=job_description,
                required_skills=skills_list,
                min_years_experience=min_years_experience,
                min_education=min_education
            ),
            score=ResumeScore(
                overall_score=score_data["overall_score"],
                skill_match_score=score_data["skill_match_score"],
                experience_score=score_data["experience_score"],
                education_score=score_data["education_score"],
                matching_skills=score_data["matching_skills"],
                missing_skills=score_data["missing_skills"],
                extra_skills=score_data["extra_skills"],
                analysis=score_data.get("analysis")
            ),
            feedback=feedback,
            improved_resume=improved_resume
        )
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        # For any other unexpected exceptions
        error_trace = traceback.format_exc()
        print(f"Unexpected error: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Warning: Failed to delete temporary file {temp_path}: {e}")

if __name__ == "__main__":
    """Run the FastAPI app with uvicorn server."""
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
