
"""
ResumeImprover Agent for Crew AI Resume Checker

This agent handles providing feedback and improving resumes.
"""

import os
import json
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
from crewai import Agent, Task

class ResumeImprover:
    """Agent for providing feedback and improving resumes."""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the ResumeImprover agent.
        
        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        self.templates_dir = templates_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def generate_feedback(self, resume_data: Dict[str, Any], score_data: Dict[str, Any]) -> str:
        """
        Generate detailed feedback on resume strengths, weaknesses, and ATS compatibility.
        
        Args:
            resume_data: Parsed resume data from ResumeParser
            score_data: Score data from ResumeScorer
            
        Returns:
            Structured feedback text with actionable recommendations
        """
        # Load the template
        template = self.jinja_env.get_template("review_and_suggest.md.j2")
        
        # Create a context with all the data needed for the template
        context = {
            "resume": resume_data,
            "score": score_data,
            "recommendations": self._generate_recommendations(resume_data, score_data)
        }
        
        # Render the template with the context data
        feedback = template.render(**context)
        
        return feedback
    
    def rewrite_resume(self, resume_data: Dict[str, Any], score_data: Dict[str, Any], feedback: str) -> str:
        """
        Produce a polished, ATS-optimized version of the resume.
        
        Args:
            resume_data: Parsed resume data from ResumeParser
            score_data: Score data from ResumeScorer
            feedback: Feedback from generate_feedback
            
        Returns:
            Plain text of improved resume
        """
        # Load the template
        template = self.jinja_env.get_template("rewrite_resume.md.j2")
        
        # Create a context with all the data needed for the template
        context = {
            "resume": resume_data,
            "score": score_data,
            "feedback": feedback,
            "missing_skills": score_data.get("missing_skills", []),
            "matching_skills": score_data.get("matching_skills", []),
            "extra_skills": score_data.get("extra_skills", [])
        }
        
        # Render the template with the context data
        rewritten_resume = template.render(**context)
        
        return rewritten_resume
    
    def _generate_recommendations(self, resume_data: Dict[str, Any], score_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate specific recommendations based on resume and score data."""
        recommendations = {
            "skills": [],
            "experience": [],
            "education": [],
            "formatting": []
        }
        
        # Skills recommendations
        missing_skills = score_data.get("missing_skills", [])
        if missing_skills:
            if len(missing_skills) > 3:
                recommendations["skills"].append(
                    f"Add these key missing skills that match the job requirements: {', '.join(missing_skills[:3])}, and others"
                )
            else:
                recommendations["skills"].append(
                    f"Add these key missing skills that match the job requirements: {', '.join(missing_skills)}"
                )
                
        if score_data.get("skill_match_score", 0) < 0.6:
            recommendations["skills"].append(
                "Reorganize skills section to highlight relevant technical and soft skills that align with the job"
            )
            
        # Experience recommendations
        if score_data.get("experience_score", 0) < 0.7:
            recommendations["experience"].append(
                "Quantify achievements with specific metrics and results"
            )
            recommendations["experience"].append(
                "Use strong action verbs to begin bullet points"
            )
            recommendations["experience"].append(
                "Focus on achievements rather than responsibilities"
            )
            
        # Check if work experience seems thin
        if len(resume_data.get("experience", [])) < 2:
            recommendations["experience"].append(
                "Expand your experience section with relevant projects, internships, or volunteer work"
            )
            
        # Education recommendations
        if score_data.get("education_score", 0) < 1.0:
            recommendations["education"].append(
                "Highlight relevant coursework or projects that demonstrate required knowledge"
            )
            recommendations["education"].append(
                "Include any additional certifications or continuing education"
            )
            
        # Formatting recommendations
        recommendations["formatting"] = [
            "Use a clean, ATS-friendly format with standard section headings",
            "Ensure proper use of keywords from the job description",
            "Remove graphics, images, and complex formatting that ATS systems can't parse",
            "Use bullet points (not paragraphs) for experience and achievements",
            "Keep to a 1-2 page limit depending on experience level"
        ]
        
        return recommendations

    def create_crew_agent(self) -> Agent:
        """Create a CrewAI agent for the ResumeImprover."""
        return Agent(
            role="Resume Improvement Specialist",
            goal="Provide actionable feedback and polished rewrites that improve candidate success rates",
            backstory="A career counselor and writer with deep knowledge of what recruiters look for in resumes",
            verbose=True,
            llm_config={
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 8000
            },
            tools=[
                self.generate_feedback,
                self.rewrite_resume
            ]
        )
        
    def define_tasks(self) -> List[Task]:
        """Define CrewAI tasks for the ResumeImprover agent."""
        return [
            Task(
                description="Generate detailed feedback on resume strengths, weaknesses, and ATS compatibility",
                agent=self.create_crew_agent(),
                expected_output="Structured feedback text with actionable recommendations",
                function=self.generate_feedback
            ),
            Task(
                description="Produce a polished, ATS-optimized version of the resume",
                agent=self.create_crew_agent(),
                expected_output="Plain text of improved resume",
                function=self.rewrite_resume
            )
        ]
