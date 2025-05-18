"""
ResumeParser Agent for Crew AI Resume Checker

This agent handles loading, extracting text from, and parsing resume files.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple, List

import PyPDF2
import docx2txt
import spacy
from crewai import Agent, Task

# Load NLP model for entity extraction
nlp = spacy.load("en_core_web_lg")

class ResumeParser:
    """Agent for parsing resumes and extracting structured information."""
    
    def __init__(self):
        """Initialize the ResumeParser agent."""
        self.supported_formats = ['.pdf', '.docx']
        # Resume validation keywords
        self.resume_indicators = [
            "experience", "education", "skills", "work", "employment", 
            "job", "career", "professional", "certification", "resume", "cv",
            "curriculum vitae", "qualification", "objective", "summary",
            "contact", "reference", "achievement", "project", "volunteer"
        ]
        
    def load_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Load a resume file and validate its format.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dict containing file metadata and binary content
        """
        file_path = Path(file_path)
        
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file format
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
            
        return {
            'filename': file_path.name,
            'format': file_path.suffix.lower(),
            'size': file_path.stat().st_size,
            'content': content
        }
    
    def extract_text(self, file_data: Dict[str, Any]) -> str:
        """
        Extract text content from a resume file.
        
        Args:
            file_data: Dict containing file metadata and binary content
            
        Returns:
            Extracted text from the resume
        """
        content = file_data['content']
        file_format = file_data['format']
        
        # Create a temporary file to process
        with tempfile.NamedTemporaryFile(suffix=file_format, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            if file_format == '.pdf':
                text = self._extract_from_pdf(temp_path)
            elif file_format == '.docx':
                text = self._extract_from_docx(temp_path)
            else:
                raise ValueError(f"Unsupported format for text extraction: {file_format}")
            
            # Validate if the document appears to be a resume
            self.validate_resume_content(text)
            
            return text
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def validate_resume_content(self, text: str) -> bool:
        """
        Validate if the document content appears to be a resume.
        
        Args:
            text: Extracted text from document
            
        Returns:
            True if valid resume, raises ValueError otherwise
        """
        text_lower = text.lower()
        
        # Check if the text has minimum length for a resume
        if len(text) < 200:
            raise ValueError("Document is too short to be a valid resume")
        
        # Check for resume indicator keywords
        indicator_count = sum(1 for indicator in self.resume_indicators if indicator in text_lower)
        
        # Document should contain at least 3 resume indicators to be considered valid
        if indicator_count < 3:
            raise ValueError(
                "The uploaded document does not appear to be a resume. "
                "Please upload a document containing education, work experience, and skills sections."
            )
        
        # Check for typical resume structure (at least some sections)
        has_experience = any(exp in text_lower for exp in ["experience", "work", "employment", "job history"])
        has_education = any(edu in text_lower for edu in ["education", "academic", "university", "college", "degree"])
        has_skills = any(skill in text_lower for skill in ["skills", "competencies", "expertise"])
        
        # Minimum structure requirements
        if not (has_experience or has_education or has_skills):
            raise ValueError(
                "The document is missing key resume sections. "
                "A proper resume should include details about experience, education, or skills."
            )
            
        return True
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        return docx2txt.process(file_path)
    
    def parse_entities(self, text: str) -> Dict[str, Any]:
        """
        Parse entities from resume text using NLP.
        
        Args:
            text: Plain text extracted from resume
            
        Returns:
            Dict containing structured information extracted from the resume
        """
        # Process the text with spaCy
        doc = nlp(text)
        
        # Extract basic entities
        entities = {
            "name": self._extract_name(doc, text),
            "contact_info": self._extract_contact_info(doc, text),
            "education": self._extract_education(doc, text),
            "skills": self._extract_skills(doc, text),
            "experience": self._extract_experience(doc, text),
            "raw_text": text
        }
        
        return entities
    
    def _extract_name(self, doc, text: str) -> str:
        """Extract candidate name from resume."""
        # Simple heuristic: First PERSON entity is likely the candidate's name
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
                
        # Fallback: First line might contain the name
        first_line = text.strip().split('\n')[0]
        return first_line if len(first_line) < 40 else "Unknown"
    
    def _extract_contact_info(self, doc, text: str) -> Dict[str, str]:
        """Extract contact information from resume."""
        contact_info = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "location": None
        }
        
        # Extract email
        for token in doc:
            if token.like_email:
                contact_info["email"] = token.text
                break
                
        # Extract phone using regex pattern matching (simplified here)
        import re
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            contact_info["phone"] = phone_matches[0]
            
        # Extract LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text.lower())
        if linkedin_matches:
            contact_info["linkedin"] = "https://www." + linkedin_matches[0]
            
        # Extract location from GPE (GeoPolitical Entity) entities
        for ent in doc.ents:
            if ent.label_ == "GPE":
                contact_info["location"] = ent.text
                break
        
        return contact_info
    
    def _extract_education(self, doc, text: str) -> List[Dict[str, Any]]:
        """Extract education history from resume."""
        education = []
        
        # Look for education section using keywords
        edu_keywords = ["education", "academic", "university", "college", "degree"]
        edu_section = self._extract_section(text, edu_keywords)
        
        if edu_section:
            # Extract degrees, institutions, dates using pattern matching
            # This is a simplified implementation
            import re
            
            # Look for degree patterns
            degree_patterns = [
                r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.|MBA|Ph\.D\.)',
                r'(Bachelor\'s|Master\'s)',
                r'(BSc|MSc|BA|MA)'
            ]
            
            # Combine patterns
            combined_pattern = '|'.join(degree_patterns)
            
            # Find potential degree mentions
            degree_matches = re.finditer(combined_pattern, edu_section)
            
            for match in degree_matches:
                # Extract surrounding context
                start_pos = max(0, match.start() - 100)
                end_pos = min(len(edu_section), match.end() + 200)
                context = edu_section[start_pos:end_pos]
                
                # Extract year if present
                year_pattern = r'(19|20)\d{2}'
                years = re.findall(year_pattern, context)
                
                # Add to education list
                education.append({
                    "degree": match.group(0),
                    "institution": self._extract_institution(context),
                    "date_range": f"{min(years, default='')} - {max(years, default='')}" if years else "",
                    "field_of_study": self._extract_field_of_study(context)
                })
        
        return education
    
    def _extract_institution(self, text: str) -> str:
        """Extract educational institution from text."""
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG" and any(edu_term in ent.text.lower() 
                                          for edu_term in ["university", "college", "institute", "school"]):
                return ent.text
        return "Unknown Institution"
    
    def _extract_field_of_study(self, text: str) -> str:
        """Extract field of study from education text."""
        fields = ["computer science", "engineering", "business", "marketing", 
                 "biology", "chemistry", "physics", "mathematics", "economics",
                 "psychology", "sociology", "history", "english", "communications"]
                 
        for field in fields:
            if field in text.lower():
                return field.title()
                
        return "Not Specified"
    
    def _extract_skills(self, doc, text: str) -> List[str]:
        """Extract skills from resume."""
        # Look for skills section
        skill_keywords = ["skills", "technical skills", "core competencies", "expertise"]
        skills_section = self._extract_section(text, skill_keywords)
        
        skills = []
        
        if skills_section:
            # Split by common separators
            for separator in [",", "•", "●", "■", "\n"]:
                if separator in skills_section:
                    raw_skills = [s.strip() for s in skills_section.split(separator)]
                    # Filter out empty strings and very long items (likely not skills)
                    skills = [s for s in raw_skills if s and len(s) < 50]
                    if skills:
                        break
                        
        # Deduplicate and clean
        clean_skills = []
        seen = set()
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen and len(skill) > 2:
                seen.add(skill_lower)
                clean_skills.append(skill)
                
        return clean_skills
    
    def _extract_experience(self, doc, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume."""
        # Look for experience section
        exp_keywords = ["experience", "employment", "work history", "professional background"]
        exp_section = self._extract_section(text, exp_keywords)
        
        experiences = []
        
        if exp_section:
            # Split experience section into potential job entries
            import re
            
            # Look for date ranges as separators
            date_pattern = r'(19|20)\d{2}\s*(-|to|–|—)\s*(19|20)\d{2}|present|current'
            date_matches = list(re.finditer(date_pattern, exp_section, re.IGNORECASE))
            
            # Process each potential job entry
            for i in range(len(date_matches)):
                start_pos = date_matches[i].start()
                end_pos = date_matches[i+1].start() if i < len(date_matches)-1 else len(exp_section)
                
                job_text = exp_section[start_pos:end_pos]
                
                # Extract job title, company, and date range
                job = {
                    "title": self._extract_job_title(job_text),
                    "company": self._extract_company(job_text),
                    "date_range": date_matches[i].group(0),
                    "description": job_text.strip()
                }
                
                experiences.append(job)
        
        return experiences
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from job description."""
        common_titles = [
            "Software Engineer", "Product Manager", "Data Scientist",
            "Marketing Manager", "Project Manager", "Sales Representative",
            "Director", "Analyst", "Developer", "Designer", "Consultant"
        ]
        
        for title in common_titles:
            if title.lower() in text.lower():
                return title
                
        # If no common title found, take the first line which might be the title
        first_line = text.strip().split('\n')[0]
        # Remove the date range if it's in the first line
        import re
        date_pattern = r'(19|20)\d{2}\s*(-|to|–|—)\s*(19|20)\d{2}|present|current'
        clean_line = re.sub(date_pattern, '', first_line, flags=re.IGNORECASE).strip()
        
        return clean_line if len(clean_line) < 50 else "Unknown Position"
    
    def _extract_company(self, text: str) -> str:
        """Extract company name from job description."""
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text
                
        return "Unknown Company"
    
    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract a section of the resume based on section keywords."""
        text_lower = text.lower()
        
        # Find the starting positions of all potential section headers
        section_positions = []
        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1:
                section_positions.append(pos)
                
        if not section_positions:
            return ""
            
        # Find the start of the section (minimum position where keyword was found)
        section_start = min(section_positions)
        
        # Find the start of the next section (common section headers)
        next_sections = ["education", "skills", "experience", "employment", 
                        "projects", "achievements", "certifications",
                        "languages", "interests", "references"]
                        
        # Remove keywords used to find this section to avoid finding the same section
        for k in keywords:
            if k in next_sections:
                next_sections.remove(k)
                
        next_section_positions = []
        for section in next_sections:
            # Look for section headers that come after the current section
            pos = text_lower.find(section, section_start + 1)
            if pos != -1:
                next_section_positions.append(pos)
                
        # If no next section found, extract until the end
        if not next_section_positions:
            return text[section_start:]
            
        # Otherwise, extract until the start of the next section
        section_end = min(next_section_positions)
        return text[section_start:section_end]

    def create_crew_agent(self) -> Agent:
        """Create a CrewAI agent for the ResumeParser."""
        return Agent(
            role="Resume Parser",
            goal="Parse resumes efficiently and extract all relevant information",
            backstory="An expert in document parsing and NLP, with specialized knowledge in resume formats",
            verbose=True,
            llm_config={
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 4000
            },
            tools=[
                self.load_resume,
                self.extract_text,
                self.parse_entities
            ]
        )
        
    def define_tasks(self) -> List[Task]:
        """Define CrewAI tasks for the ResumeParser agent."""
        return [
            Task(
                description="Load a resume file (PDF or DOCX)",
                agent=self.create_crew_agent(),
                expected_output="Raw binary data of the resume file",
                function=self.load_resume
            ),
            Task(
                description="Convert resume file to raw text",
                agent=self.create_crew_agent(),
                expected_output="Plain text content of the resume",
                function=self.extract_text
            ),
            Task(
                description="Extract structured information from resume text using NLP",
                agent=self.create_crew_agent(),
                expected_output="JSON object with parsed resume data (contact info, education, skills, etc.)",
                function=self.parse_entities
            )
        ]
