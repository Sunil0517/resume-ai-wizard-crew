
# AI-Powered Resume Checker with Crew AI

This project implements an AI-powered resume checker using Crew AI agents to analyze resumes against job requirements, provide feedback, and generate improved versions optimized for ATS systems.
<img width="668" alt="Screenshot 2025-05-16 at 12 13 33 AM" src="https://github.com/user-attachments/assets/6a2e08f0-5a42-4196-9596-b315f7ff1e2c" />

## Features

- **Resume Parsing**: Extract structured data from PDF and DOCX resumes
- **Job Requirements Matching**: Compare resumes against specific job requirements
- **Score Calculation**: Generate match scores based on skills, experience, and education
- **Detailed Feedback**: Provide actionable recommendations to improve job application success
- **Resume Rewriting**: Generate ATS-optimized versions of resumes
- **Modern UI**: Responsive interface for both desktop and mobile

## Architecture

The application is built using:

- **Backend**: Python with FastAPI and Crew AI
- **Frontend**: React with TypeScript and shadcn/ui components
- **AI Integration**: OpenAI's GPT models via Crew AI

## Project Structure

```
├── agents/                 # Python agent modules for Crew AI
│   ├── resume_parser.py    # Resume parsing agent
│   ├── resume_scorer.py    # Resume scoring agent 
│   └── resume_improver.py  # Resume improvement agent
├── templates/              # Jinja2 templates for AI outputs
│   ├── review_and_suggest.md.j2  # Template for feedback generation
│   └── rewrite_resume.md.j2      # Template for resume rewriting
├── app.py                  # FastAPI application server
├── tasks.yaml              # Crew AI task definitions
├── src/                    # React frontend code
│   ├── components/         # React components
│   └── pages/              # React pages
└── README.md               # This documentation
```

## Setup Instructions

### Backend Setup

1. Install Python dependencies:

```bash
pip install crewai fastapi uvicorn python-multipart jinja2 spacy docx2txt PyPDF2
python -m spacy download en_core_web_lg
```

2. Create required directories:

```bash
mkdir -p templates
mkdir -p agents
mkdir -p frontend
```

3. Place the Python agent files in the `agents/` directory and the Jinja2 templates in the `templates/` directory.

4. Run the FastAPI server:

```bash
python app.py
```

### Frontend Setup

1. Install Node.js dependencies:

```bash
npm install
```

2. Update API endpoint in `src/pages/Index.tsx` to point to your backend server.

3. Start the development server:

```bash
npm run dev
```

## API Endpoints

- `GET /api/jobs` - List all available job positions
- `GET /api/jobs/{job_id}` - Get details for a specific job
- `POST /api/check-resume` - Upload and analyze a resume against a job

### Example API Call

```javascript
// Upload and analyze a resume
const formData = new FormData();
formData.append('resume', resumeFile);
formData.append('job_id', 'job1');

const response = await fetch('/api/check-resume', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

## Integration Guide

### Integrating the Backend with a Node.js Frontend

1. **Backend API Setup**:
   - Ensure CORS is properly configured in the FastAPI app
   - Set up proper error handling and validation
   - Implement authentication if needed

2. **Frontend Integration**:
   - Use `fetch` or Axios to make API calls to the Python backend
   - Handle file uploads with FormData
   - Implement proper loading states and error handling

3. **Deployment Considerations**:
   - Deploy the Python backend and Node.js frontend separately
   - Use a reverse proxy (like Nginx) to route requests
   - Set up environment variables for configuration

### Extending the System

To add new features:

1. **Add a new Agent**:
   - Create a new Python class in the `agents/` directory
   - Implement the required methods
   - Add the agent to the Crew AI configuration in `tasks.yaml`

2. **Add a new API Endpoint**:
   - Define the endpoint in `app.py`
   - Implement the endpoint handler
   - Update the frontend to use the new endpoint

3. **Add new UI Components**:
   - Create new React components in the `src/components/` directory
   - Use shadcn/ui for consistent styling
   - Update the pages to use the new components

## Customization Options

- **Model Selection**: Change the LLM model in `tasks.yaml` to use different OpenAI models
- **Scoring Weights**: Adjust the weights in `resume_scorer.py` to prioritize different aspects
- **Templates**: Modify the Jinja2 templates to change the feedback and rewritten resume formats
- **UI Theme**: Update the Tailwind theme in `tailwind.config.js`

## Limitations and Future Improvements

- Add support for more resume formats (HTML, JSON)
- Implement user accounts to save results and track improvements
- Add support for custom job descriptions
- Integrate with job boards and applicant tracking systems
- Add multi-language support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Crew AI](https://github.com/joaomdmoura/crewai) for the multi-agent framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- [React](https://reactjs.org/) for the frontend
- [shadcn/ui](https://ui.shadcn.com/) for UI components
- [OpenAI](https://openai.com/) for the LLM models
