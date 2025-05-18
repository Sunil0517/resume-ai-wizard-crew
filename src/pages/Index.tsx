import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { ResumeUploader } from "@/components/ResumeUploader";
import { JobSelector } from "@/components/JobSelector";
import { ResumeScore } from "@/components/ResumeScore";
import { FeedbackCard } from "@/components/FeedbackCard";
import { ImprovedResume } from "@/components/ImprovedResume";
import { ParsedResume } from "@/components/ParsedResume";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import JobRolesManager from "@/components/JobRolesManager";

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedJob, setSelectedJob] = useState<string>("job1");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [result, setResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<string>("standard-jobs");
  const { toast } = useToast();
  const formRef = useRef<HTMLFormElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFile) {
      toast({
        title: "Error",
        description: "Please upload a resume file",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setCurrentStep(1);

    // Create form data
    const formData = new FormData();
    formData.append("resume", selectedFile);
    formData.append("job_id", selectedJob);

    try {
      // Determine which API endpoint to use based on job ID source
      const endpoint = selectedJob.startsWith("custom-") ? "/api/check-resume" : "/api/check-resume";
      
      // In a real application, make the actual API call
      // const response = await fetch(endpoint, {
      //   method: "POST",
      //   body: formData,
      // });
      // const data = await response.json();

      // Simulate processing time with steps
      await simulateProcessing();
      
      // Mock response data
      const mockData = await getMockResponse(selectedJob);
      
      setResult(mockData);
      toast({
        title: "Success!",
        description: "Your resume has been analyzed",
      });
    } catch (error) {
      console.error("Error processing resume:", error);
      toast({
        title: "Error",
        description: "Failed to process your resume. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      setCurrentStep(0);
    }
  };

  const simulateProcessing = async () => {
    // Simulate processing steps
    const steps = [
      "Parsing resume...",
      "Extracting information...",
      "Analyzing against job requirements...",
      "Calculating match score...",
      "Generating feedback...",
      "Creating improved version...",
    ];

    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i + 1);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  };

  const getMockResponse = async (jobId: string) => {
    // Mock job data
    const jobs: Record<string, any> = {
      job1: {
        id: "job1",
        title: "Senior Software Engineer",
        required_skills: ["Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes"],
        min_years_experience: 5,
        min_education: "Bachelor's degree"
      },
      job2: {
        id: "job2",
        title: "Data Scientist",
        required_skills: ["Python", "SQL", "Machine Learning", "Pandas", "PyTorch", "Statistics"],
        min_years_experience: 3,
        min_education: "Master's degree"
      },
      job3: {
        id: "job3",
        title: "Product Manager",
        required_skills: ["Agile", "JIRA", "User Stories", "Roadmap Planning", "Stakeholder Management"],
        min_years_experience: 4,
        min_education: "Bachelor's degree"
      }
    };

    // Mock parsed resume (would come from backend)
    const parsedResume = {
      name: "Alex Johnson",
      contact_info: {
        email: "alex.johnson@example.com",
        phone: "(555) 123-4567",
        linkedin: "linkedin.com/in/alexjohnson",
        location: "San Francisco, CA"
      },
      education: [
        {
          degree: "Bachelor of Science",
          institution: "University of California, Berkeley",
          date_range: "2014 - 2018",
          field_of_study: "Computer Science"
        }
      ],
      skills: ["Python", "JavaScript", "React", "Node.js", "Git", "SQL", "Agile"],
      experience: [
        {
          title: "Software Engineer",
          company: "Tech Solutions Inc.",
          date_range: "2018 - 2021",
          description: "Developed and maintained web applications using React and Node.js.\nCollaborated with cross-functional teams to implement new features.\nImproved application performance by 30% through code optimization."
        },
        {
          title: "Junior Developer",
          company: "StartUp Co",
          date_range: "2016 - 2018",
          description: "Built and tested features for mobile applications.\nParticipated in code reviews and team meetings.\nAssisted in deploying applications to production environments."
        }
      ]
    };

    // Generate score based on selected job
    let score;
    if (jobId === "job1") {
      score = {
        overall_score: 0.72,
        skill_match_score: 0.65,
        experience_score: 0.60,
        education_score: 1.0,
        matching_skills: ["Python", "JavaScript", "React"],
        missing_skills: ["AWS", "Docker", "Kubernetes"],
        extra_skills: ["Node.js", "Git", "SQL", "Agile"]
      };
    } else if (jobId === "job2") {
      score = {
        overall_score: 0.51,
        skill_match_score: 0.33,
        experience_score: 0.40,
        education_score: 0.90,
        matching_skills: ["Python", "SQL"],
        missing_skills: ["Machine Learning", "Pandas", "PyTorch", "Statistics"],
        extra_skills: ["JavaScript", "React", "Node.js", "Git", "Agile"]
      };
    } else {
      score = {
        overall_score: 0.68,
        skill_match_score: 0.60,
        experience_score: 0.55,
        education_score: 0.95,
        matching_skills: ["Agile"],
        missing_skills: ["JIRA", "User Stories", "Roadmap Planning", "Stakeholder Management"],
        extra_skills: ["Python", "JavaScript", "React", "Node.js", "Git", "SQL"]
      };
    }

    return {
      parsed_resume: parsedResume,
      job_data: jobs[jobId],
      score,
      feedback: `# Resume Review for Alex Johnson\n\n## Overall Score: ${Math.round(score.overall_score * 100)}%\n\n### Score Breakdown:\n- **Skills Match**: ${Math.round(score.skill_match_score * 100)}%\n- **Experience**: ${Math.round(score.experience_score * 100)}%\n- **Education**: ${Math.round(score.education_score * 100)}%\n\n## Resume Strengths\n\n### Key Matching Skills:\n${score.matching_skills.map(skill => `- ${skill}`).join('\n')}\n\n### Experience Highlights:\n- Software Engineer at Tech Solutions Inc.\n- Junior Developer at StartUp Co\n\n### Education Achievements:\n- Bachelor of Science from University of California, Berkeley\n\n## Areas for Improvement\n\n### Missing Key Skills:\n${score.missing_skills.map(skill => `- ${skill}`).join('\n')}\n\n### Skills Gaps:\nYour resume currently shows a ${Math.round(score.skill_match_score * 100)}% match with the required skills for this position. Consider addressing the missing skills listed above.\n\n### Experience Enhancement:\nYour experience level appears to be below the job requirements. Consider highlighting more relevant achievements and quantifiable results.\n\n## ATS Optimization Recommendations\n\n### Content Recommendations:\n- Add these key missing skills that match the job requirements: ${score.missing_skills.slice(0, 3).join(', ')}, and others\n- Reorganize skills section to highlight relevant technical and soft skills that align with the job\n- Quantify achievements with specific metrics and results\n- Use strong action verbs to begin bullet points\n- Focus on achievements rather than responsibilities\n\n### Formatting Recommendations:\n- Use a clean, ATS-friendly format with standard section headings\n- Ensure proper use of keywords from the job description\n- Remove graphics, images, and complex formatting that ATS systems can't parse\n- Use bullet points (not paragraphs) for experience and achievements\n- Keep to a 1-2 page limit depending on experience level\n\n## Next Steps\n\n1. Update your resume using the recommendations above\n2. Tailor your skills section to better match job requirements\n3. Quantify achievements with specific metrics and results\n4. Use keywords from the job description throughout your resume\n5. Ensure your resume is formatted for ATS compatibility\n\n*This review was generated by our AI-powered resume checker to help improve your job application success rate.*`,
      improved_resume: `# ALEX JOHNSON\n\nalex.johnson@example.com | (555) 123-4567\nlinkedin.com/in/alexjohnson | San Francisco, CA\n\n## PROFESSIONAL SUMMARY\n\nResults-driven software engineer with significant experience in web application development. Proven track record of developing and maintaining web applications using React and Node.js. Skilled in Python, JavaScript, React with growing expertise in AWS, Docker, Kubernetes.\n\n## SKILLS\n\n**Core Skills:** Python, JavaScript, React\n\n**Additional Skills:** Node.js, Git, SQL, Agile\n\n**Developing Skills:** AWS, Docker, Kubernetes\n\n## PROFESSIONAL EXPERIENCE\n\n### SOFTWARE ENGINEER | TECH SOLUTIONS INC.\n*2018 - 2021*\n\n- Developed and maintained web applications using React and Node.js Leveraged Python to deliver measurable results.\n- Collaborated with cross-functional teams to implement new features\n- Improved application performance by 30% through code optimization\n- Implemented CI/CD pipelines to streamline deployment processes\n- Mentored junior developers and conducted code reviews\n\n### JUNIOR DEVELOPER | STARTUP CO\n*2016 - 2018*\n\n- Built and tested features for mobile applications\n- Participated in code reviews and team meetings\n- Assisted in deploying applications to production environments\n- Developed RESTful APIs using Node.js and Express\n- Implemented responsive UI components with React\n\n## EDUCATION\n\n### BACHELOR OF SCIENCE IN COMPUTER SCIENCE\n*University of California, Berkeley | 2014 - 2018*\n\n## TECHNICAL PROFICIENCIES\n\n**Programming:** Python, JavaScript\n**Tools:** Git, SQL\n**Platforms:** React, Node.js\n**Other:** Agile\n\n## CERTIFICATIONS & ADDITIONAL TRAINING\n\n- AWS Certified Developer Associate (In Progress)\n- Docker and Kubernetes Fundamentals (Online Course)\n\n*This resume has been optimized for ATS systems while highlighting the most relevant skills and experiences for the target position.*`
    };
  };

  // Handle selection of a custom job role
  const handleSelectCustomJob = (jobId: string) => {
    setSelectedJob(jobId);
    setActiveTab("standard-jobs"); // Switch back to the main tab after selection
    
    toast({
      title: "Custom Job Selected",
      description: `Using your custom job role for resume analysis.`,
    });
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">AI Resume Checker</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <form ref={formRef} onSubmit={handleSubmit} className="space-y-8">
            <ResumeUploader 
              selectedFile={selectedFile} 
              onFileChange={(file) => setSelectedFile(file)} 
            />
            
            <Card>
              <CardHeader>
                <CardTitle>Step 2: Select Job</CardTitle>
                <CardDescription>
                  Choose a job to match your resume against
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="w-full">
                    <TabsTrigger value="standard-jobs">Standard Jobs</TabsTrigger>
                    <TabsTrigger value="custom-jobs">Custom Job Roles</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="standard-jobs">
                    <JobSelector 
                      selectedJob={selectedJob} 
                      onJobChange={(job) => setSelectedJob(job)} 
                    />
                  </TabsContent>
                  
                  <TabsContent value="custom-jobs">
                    <JobRolesManager onSelectJob={handleSelectCustomJob} />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
            
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center">
                  <LoadingSpinner  />
                  Processing...
                </span>
              ) : (
                "Check Resume"
              )}
            </Button>
            
            {isLoading && (
              <div className="space-y-2">
                <Progress value={currentStep * 16.67} className="h-2" />
                <p className="text-sm text-center">
                  {[
                    "Parsing resume...",
                    "Extracting information...",
                    "Analyzing against job requirements...",
                    "Calculating match score...",
                    "Generating feedback...",
                    "Creating improved version..."
                  ][currentStep - 1]}
                </p>
              </div>
            )}
          </form>
        </div>
        
        <div>
          {result ? (
            <Tabs defaultValue="score" className="w-full">
              <TabsList className="w-full">
                <TabsTrigger value="score">Match Score</TabsTrigger>
                <TabsTrigger value="feedback">Feedback</TabsTrigger>
                <TabsTrigger value="improved">Improved Resume</TabsTrigger>
                <TabsTrigger value="parsed">Parsed Data</TabsTrigger>
              </TabsList>
              <TabsContent value="score">
                <ResumeScore score={result.score} jobData={result.job_data} />
              </TabsContent>
              <TabsContent value="feedback">
                <FeedbackCard feedback={result.feedback} />
              </TabsContent>
              <TabsContent value="improved">
                <ImprovedResume content={result.improved_resume} />
              </TabsContent>
              <TabsContent value="parsed">
                <ParsedResume data={result.parsed_resume} />
              </TabsContent>
            </Tabs>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Resume Analysis</CardTitle>
                <CardDescription>
                  Upload your resume and select a job to get started
                </CardDescription>
              </CardHeader>
              <CardContent className="min-h-[300px] flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <p>Your resume analysis results will appear here</p>
                  <Button
                    variant="link"
                    onClick={() => {
                      const demoResult = getMockResponse("job1");
                      setSelectedJob("job1");
                      demoResult.then(data => setResult(data));
                    }}
                  >
                    See Demo Result
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Index;
