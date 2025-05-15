
"""
ResumeScorer Agent for Crew AI Resume Checker

This agent handles fetching job requirements and scoring resumes against those requirements.
"""

import json
import requests
from typing import Dict, Any, List
from crewai import Agent, Task

class ResumeScorer:
    """Agent for scoring resumes against job requirements."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the ResumeScorer agent.
        
        Args:
            api_base_url: Base URL for the job requirements API
        """
        self.api_base_url = api_base_url
        
    def fetch_job(self, job_id: str) -> Dict[str, Any]:
        """
        Fetch job requirements from the API.
        
        Args:
            job_id: ID of the job to fetch
            
        Returns:
            Dict containing job requirements data
        """
        endpoint = f"{self.api_base_url}/api/jobs/{job_id}"
        
        try:
            response = requests.get(endpoint)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            return response.json()
        except requests.RequestException as e:
            # Handle specific HTTP errors
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    raise ValueError(f"Job with ID {job_id} not found")
                elif e.response.status_code == 401:
                    raise ValueError("Unauthorized access to job API")
                else:
                    raise ValueError(f"Error fetching job: HTTP {e.response.status_code}")
            else:
                # Handle connection errors
                raise ValueError(f"Connection error: {str(e)}")
    
    def compute_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate weighted fit score between resume and job requirements.
        
        Args:
            resume_data: Parsed resume data from ResumeParser
            job_data: Job requirements data from fetch_job
            
        Returns:
            Dict containing overall and component scores
        """
        # Extract relevant information from resume and job data
        resume_skills = set(s.lower() for s in resume_data.get("skills", []))
        job_skills = set(s.lower() for s in job_data.get("required_skills", []))
        
        # Calculate skill match score (40% weight)
        skill_match_score = self._calculate_skill_match(resume_skills, job_skills)
        
        # Calculate experience match score (30% weight)
        experience_score = self._calculate_experience_match(
            resume_data.get("experience", []),
            job_data.get("min_years_experience", 0)
        )
        
        # Calculate education match score (30% weight)
        education_score = self._calculate_education_match(
            resume_data.get("education", []),
            job_data.get("min_education", "")
        )
        
        # Calculate overall weighted score
        overall_score = (
            0.4 * skill_match_score +
            0.3 * experience_score +
            0.3 * education_score
        )
        
        # Return detailed score breakdown
        return {
            "overall_score": round(overall_score, 2),
            "skill_match_score": round(skill_match_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "matching_skills": list(resume_skills.intersection(job_skills)),
            "missing_skills": list(job_skills - resume_skills),
            "extra_skills": list(resume_skills - job_skills)
        }
    
    def _calculate_skill_match(self, resume_skills: set, job_skills: set) -> float:
        """Calculate skill match score between resume skills and job skills."""
        if not job_skills:
            return 1.0  # Perfect score if no skills required
            
        # Count matching skills
        matching_skills = resume_skills.intersection(job_skills)
        
        # Calculate Jaccard similarity with a bonus for matching required skills
        if len(resume_skills) == 0:
            return 0.0
            
        # Base score is percentage of required skills that match
        base_score = len(matching_skills) / len(job_skills)
        
        # Bonus for having more relevant skills (up to +20%)
        skill_bonus = min(0.2, len(matching_skills) / len(resume_skills) * 0.2)
        
        # Penalty for having too many irrelevant skills (up to -10%)
        irrelevant_penalty = 0
        if len(resume_skills) > 2 * len(job_skills):
            irrelevant_penalty = min(0.1, (len(resume_skills - job_skills) / len(job_skills)) * 0.1)
            
        return min(1.0, max(0.0, base_score + skill_bonus - irrelevant_penalty))
    
    def _calculate_experience_match(self, experience: List[Dict[str, Any]], min_years: int) -> float:
        """Calculate experience match score based on years of experience."""
        if min_years <= 0:
            return 1.0  # Perfect score if no experience required
            
        # Estimate total years of experience
        total_years = 0
        for job in experience:
            # Extract years from date range
            date_range = job.get("date_range", "")
            years = self._extract_years_from_date_range(date_range)
            total_years += years
            
        # Calculate score based on ratio of actual to required experience
        if total_years >= min_years:
            return 1.0  # Perfect score if meets or exceeds requirements
        elif total_years <= 0:
            return 0.0  # No score if no experience
        else:
            return total_years / min_years  # Partial score based on ratio
    
    def _extract_years_from_date_range(self, date_range: str) -> float:
        """Extract years of experience from a date range string."""
        import re
        from datetime import datetime
        
        # Look for patterns like "2018 - 2022" or "2018 - Present"
        pattern = r'(\d{4})\s*(-|to|–|—)\s*(\d{4}|present|current)'
        match = re.search(pattern, date_range, re.IGNORECASE)
        
        if not match:
            return 0
            
        start_year = int(match.group(1))
        end_str = match.group(3).lower()
        
        # Handle "present" or "current"
        if end_str in ["present", "current"]:
            end_year = datetime.now().year
        else:
            end_year = int(end_str)
            
        # Calculate years (including partial years)
        years = end_year - start_year
        
        # Cap at reasonable maximum per position
        return min(years, 10)
    
    def _calculate_education_match(self, education: List[Dict[str, Any]], min_education: str) -> float:
        """Calculate education match score based on degree level."""
        if not min_education:
            return 1.0  # Perfect score if no education requirement
            
        # Define education levels and their numeric values
        education_levels = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5,
            "doctorate": 5
        }
        
        # Determine required education level
        required_level = 0
        for level_name, level_value in education_levels.items():
            if level_name in min_education.lower():
                required_level = level_value
                break
                
        # If no valid requirement found
        if required_level == 0:
            return 1.0
            
        # Determine highest education level in resume
        highest_level = 0
        for edu in education:
            degree = edu.get("degree", "").lower()
            for level_name, level_value in education_levels.items():
                if level_name in degree:
                    highest_level = max(highest_level, level_value)
                    
        # Calculate score
        if highest_level >= required_level:
            return 1.0  # Perfect score if meets or exceeds requirements
        elif highest_level == 0:
            return 0.0  # No score if no education found
        else:
            # Partial credit based on how close the education level is
            return highest_level / required_level
            
    def create_crew_agent(self) -> Agent:
        """Create a CrewAI agent for the ResumeScorer."""
        return Agent(
            role="Resume Evaluator",
            goal="Calculate accurate matching scores between resumes and job requirements",
            backstory="A meticulous analyst with expertise in matching candidate qualifications to job requirements",
            verbose=True,
            llm_config={
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            tools=[
                self.fetch_job,
                self.compute_score
            ]
        )
        
    def define_tasks(self) -> List[Task]:
        """Define CrewAI tasks for the ResumeScorer agent."""
        return [
            Task(
                description="Retrieve job requirements from external API",
                agent=self.create_crew_agent(),
                expected_output="JSON object with job requirements data",
                function=self.fetch_job
            ),
            Task(
                description="Calculate weighted fit score between resume and job requirements",
                agent=self.create_crew_agent(),
                expected_output="JSON object with overall and component scores",
                function=self.compute_score
            )
        ]
