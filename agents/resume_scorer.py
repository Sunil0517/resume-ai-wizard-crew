"""
ResumeScorer Agent for Crew AI Resume Checker

This agent handles fetching job requirements and scoring resumes against those requirements.
"""

import json
import requests
import re
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
        # Validate input data structure
        self._validate_input_data(resume_data, job_data)
        
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
            "extra_skills": list(resume_skills - job_skills),
            "analysis": self._generate_score_analysis(
                skill_match_score, 
                experience_score, 
                education_score, 
                resume_skills.intersection(job_skills),
                job_skills - resume_skills
            )
        }
    
    def _validate_input_data(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> None:
        """
        Validate that input data contains required fields.
        
        Args:
            resume_data: Parsed resume data
            job_data: Job requirements data
            
        Raises:
            ValueError: If required data is missing
        """
        # Check if resume data has minimal required sections
        if not resume_data.get("skills") and not resume_data.get("experience") and not resume_data.get("education"):
            raise ValueError("Resume data is missing critical sections (skills, experience, education)")
            
        # Check if job data has minimal required fields
        if "title" not in job_data or "required_skills" not in job_data:
            raise ValueError("Job data is missing critical fields (title, required_skills)")
    
    def _calculate_skill_match(self, resume_skills: set, job_skills: set) -> float:
        """Calculate skill match score between resume skills and job skills."""
        if not job_skills:
            return 0.85  # No skills listed, but don't give perfect score
            
        if not resume_skills:
            return 0.0  # No skills extracted from resume
            
        # Count matching skills
        matching_skills = resume_skills.intersection(job_skills)
        
        # Core skill match ratio (this is the most important factor)
        skill_match_ratio = len(matching_skills) / len(job_skills) if job_skills else 0
        
        # Weight factors
        core_weight = 0.7  # How much of the score depends on matching required skills
        breadth_weight = 0.2  # Bonus for having additional relevant skills
        precision_weight = 0.1  # Penalty for having too many irrelevant skills
        
        # Calculate breadth score (bonus for having more relevant skills)
        # We want a higher score if resume has many matching skills compared to its total skills
        breadth_score = len(matching_skills) / max(len(resume_skills), 1) if resume_skills else 0
        
        # Calculate precision score (penalty for having too many irrelevant skills)
        # Lower score if many skills on resume don't match job requirements
        irrelevant_skills = len(resume_skills - job_skills)
        precision_score = 1.0 - (irrelevant_skills / max(len(resume_skills) + len(job_skills), 1))
        precision_score = max(0, precision_score)  # Ensure non-negative
        
        # Combine scores with weights
        combined_score = (
            core_weight * skill_match_ratio + 
            breadth_weight * breadth_score + 
            precision_weight * precision_score
        )
        
        # Scale to ensure score is between 0 and 1
        return min(1.0, max(0.0, combined_score))
    
    def _calculate_experience_match(self, experience: List[Dict[str, Any]], min_years: int) -> float:
        """Calculate experience match score based on years of experience."""
        if min_years <= 0:
            return 0.9  # High score if no experience required, but not perfect
            
        # Check if experience data is available
        if not experience:
            return 0.0  # No experience data available
            
        # Estimate total years of experience
        total_years = 0
        relevant_years = 0
        
        for job in experience:
            # Extract years from date range
            date_range = job.get("date_range", "")
            years = self._extract_years_from_date_range(date_range)
            
            # Count towards total experience
            total_years += years
            
            # Check for relevance based on job title/description
            # This is a simplified relevance check
            if self._check_experience_relevance(job):
                relevant_years += years
            
        # Calculate score based on a combination of total and relevant experience
        total_score = min(1.0, total_years / min_years) if min_years > 0 else 1.0
        relevant_score = min(1.0, relevant_years / min_years) if min_years > 0 else 1.0
        
        # Weight relevant experience more heavily
        combined_score = 0.3 * total_score + 0.7 * relevant_score
        
        return min(1.0, max(0.0, combined_score))
    
    def _check_experience_relevance(self, job: Dict[str, Any]) -> bool:
        """
        Check if a job experience appears relevant to the position.
        This is a simplified check - in production this would be more sophisticated.
        """
        # Implementation would compare job title and description to the target role
        # For now, assume most recent jobs are more relevant
        return True  # Simplified implementation
    
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
            return 0.9  # High score if no education requirement, but not perfect
            
        # Check if education data is available
        if not education:
            return 0.0
            
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
            return 0.85
            
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
            
    def _generate_score_analysis(self, skill_score: float, exp_score: float, edu_score: float, 
                               matching_skills: set, missing_skills: set) -> str:
        """Generate a textual analysis of the scoring results."""
        analysis = []
        
        # Overall assessment
        average_score = (skill_score + exp_score + edu_score) / 3
        if average_score >= 0.8:
            analysis.append("The resume is a strong match for this position.")
        elif average_score >= 0.6:
            analysis.append("The resume shows moderate alignment with the position requirements.")
        else:
            analysis.append("The resume needs significant improvements to be competitive for this role.")
        
        # Skills assessment
        if skill_score >= 0.8:
            analysis.append("Skills are well-matched to the requirements.")
        elif skill_score >= 0.5:
            analysis.append(f"Some key skills match, but {len(missing_skills)} required skills are missing.")
        else:
            analysis.append("The resume lacks many of the key skills required for this position.")
        
        # Experience assessment
        if exp_score >= 0.8:
            analysis.append("Experience level meets or exceeds requirements.")
        elif exp_score >= 0.5:
            analysis.append("Experience is partially aligned with requirements, but may need more depth.")
        else:
            analysis.append("The resume shows insufficient experience for this role.")
        
        # Education assessment
        if edu_score >= 0.8:
            analysis.append("Education credentials are suitable for this position.")
        elif edu_score >= 0.5:
            analysis.append("Education partially meets requirements but may be insufficient.")
        else:
            analysis.append("Education falls short of the minimum requirements for this position.")
            
        return " ".join(analysis)
    
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
