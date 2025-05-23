
import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { ResumeUploader } from "@/components/ResumeUploader";
import { ResumeScore } from "@/components/ResumeScore";
import { FeedbackCard } from "@/components/FeedbackCard";
import { ImprovedResume } from "@/components/ImprovedResume";
import { ParsedResume } from "@/components/ParsedResume";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import JobRolesManager from "@/components/JobRolesManager";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from "@/components/ui/dialog";
import { CheckCircle2, Circle, ArrowRight } from "lucide-react";

// Processing steps for the modal
const PROCESS_STEPS = [
  {
    title: "Parsing resume",
    description: "Extracting text content from your uploaded document"
  },
  {
    title: "Extracting information",
    description: "Identifying key details like skills, experience, and education"
  },
  {
    title: "Analyzing against requirements",
    description: "Comparing your resume against the job requirements"
  },
  {
    title: "Calculating match score",
    description: "Determining how well your resume matches the job"
  },
  {
    title: "Generating feedback",
    description: "Creating personalized improvement suggestions"
  },
  {
    title: "Creating improved version",
    description: "Building an optimized version of your resume"
  }
];

// Create a fetch with timeout function
const fetchWithTimeout = async (url, options, timeout = 60000) => {
  const controller = new AbortController();
  const signal = controller.signal;
  
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, { ...options, signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedJob, setSelectedJob] = useState<string>("custom");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [result, setResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<string>("standard-jobs");
  const { toast } = useToast();
  const formRef = useRef<HTMLFormElement>(null);
  const [customJobData, setCustomJobData] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFile) {
      toast({
        title: "No Resume Selected",
        description: "Please upload a resume file before checking",
        variant: "destructive",
      });
      return;
    }

    if (!customJobData) {
      toast({
        title: "Job Requirements Missing",
        description: "Please fill in the job requirements first",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setCurrentStep(1);

    // Create form data
    const formData = new FormData();
    formData.append("resume", selectedFile);
    formData.append("job_title", customJobData.title || "");
    formData.append("job_description", customJobData.description || "");
    formData.append("required_skills", (customJobData.required_skills || []).join(", "));
    formData.append("min_years_experience", String(customJobData.min_years_experience || 0));
    formData.append("min_education", customJobData.min_education || "Bachelor's degree");
    
    // Progress update promise - will show steps regardless of API response
    const progressPromise = updateProgressSteps();
    
    try {
      console.log("Submitting form data:", {
        job_title: customJobData.title,
        required_skills: (customJobData.required_skills || []).join(", "),
        min_years_experience: customJobData.min_years_experience,
        min_education: customJobData.min_education
      });
      
      // Make the actual API request with timeout (60 seconds)
      const response = await fetchWithTimeout("/api/analyze-resume-with-requirements", {
        method: 'POST',
        body: formData,
      }, 60000);
      
      if (!response.ok) {
        // Try to get error details from response
        let errorMessage = `Server error: ${response.status} ${response.statusText}`;
        try {
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const errorData = await response.json();
            if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          } else {
            // If not JSON, try to get text response
            const textError = await response.text();
            if (textError) {
              errorMessage += ` - ${textError.substring(0, 100)}${textError.length > 100 ? '...' : ''}`;
            }
          }
        } catch (parseError) {
          console.error("Error parsing error response:", parseError);
        }
        throw new Error(errorMessage);
      }
      
      // Check content type
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error(`Expected JSON response but got: ${contentType}`);
      }
      
      // Get response text first for debugging
      const responseText = await response.text();
      
      // Try parsing the JSON
      let realData;
      try {
        realData = JSON.parse(responseText);
      } catch (jsonError) {
        console.error("JSON parsing error:", jsonError);
        console.error("Raw response:", responseText);
        throw new Error(`Failed to parse JSON response: ${jsonError.message}`);
      }
      
      // Ensure we have complete data structure
      if (!realData || !realData.parsed_resume || !realData.score) {
        console.error("Incomplete response data:", realData);
        throw new Error("Incomplete data received from server");
      }
      
      // Update the result with the real data
      setResult(realData);
      toast({
        title: "Success!",
        description: "Your resume has been analyzed",
      });
    } catch (error) {
      console.error("Error processing resume:", error);
      let errorMessage = "Failed to process your resume. Please try again.";
      
      if (error.name === 'AbortError') {
        errorMessage = "Request timed out. The server took too long to respond.";
      } else if (typeof error === 'object' && error !== null) {
        errorMessage = error.message || errorMessage;
      }
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      // Wait for progress steps to complete for better UX
      await progressPromise;
      setIsLoading(false);
      setCurrentStep(0);
    }
  };

  // Update progress steps while waiting for API response
  const updateProgressSteps = async () => {
    // Update steps with realistic timing based on processing complexity
    const stepDurations = [1500, 2000, 3000, 1500, 2500, 2500]; // milliseconds per step
    
    for (let i = 0; i < PROCESS_STEPS.length; i++) {
      setCurrentStep(i + 1);
      await new Promise(resolve => setTimeout(resolve, stepDurations[i]));
    }
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
            {/* Resume Upload Card */}
            <Card>
              <CardHeader>
                <CardTitle>Upload Your Resume</CardTitle>
                <CardDescription>
                  Upload your resume to analyze against job requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResumeUploader 
                  selectedFile={selectedFile} 
                  onFileChange={(file) => setSelectedFile(file)} 
                />
              </CardContent>
            </Card>
            
            {/* Job Requirements Card */}
            <Card>
              <CardHeader>
                <CardTitle>Job Requirements</CardTitle>
                <CardDescription>
                  Define job requirements to match against your resume
                </CardDescription>
              </CardHeader>
              <CardContent>
                <JobRolesManager 
                  onSubmitCustomJob={(jobDetails) => {
                    // Create a custom job data object with default values for any missing fields
                    const customJobData = {
                      id: "custom",
                      title: jobDetails.title || "Job Title",
                      description: jobDetails.description || "",
                      required_skills: jobDetails.requiredSkills || [],
                      min_years_experience: parseInt(String(jobDetails.minYearsExperience || 0)),
                      min_education: jobDetails.minEducation || "Bachelor's degree"
                    };
                    
                    // Save the custom job data to state
                    setCustomJobData(customJobData);
                    
                    // Set it as the selected job
                    setSelectedJob("custom");
                  }} 
                />
              </CardContent>
            </Card>
            
            {/* Analysis Button */}
            <Button 
              type="submit" 
              className="w-full py-6 text-lg" 
              disabled={isLoading || !selectedFile || !customJobData}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <LoadingSpinner className="mr-2" />
                  <span>Processing...</span>
                </span>
              ) : (
                "Analyse Resume"
              )}
            </Button>
            
            {isLoading && (
              <Dialog open={isLoading} onOpenChange={(open) => !open && setIsLoading(false)}>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle className="text-center text-xl">Processing Your Resume</DialogTitle>
                    <DialogDescription className="text-center">
                      Please wait while we analyze your resume
                    </DialogDescription>
                  </DialogHeader>
                  <div className="flex flex-col space-y-6 py-4">
                    <div className="relative">
                      <Progress value={currentStep * 16.67} className="h-2" />
                      <div className="mt-1 text-right text-xs text-muted-foreground">
                        Step {currentStep} of 6
                      </div>
                    </div>
                    
                    <div className="space-y-5 max-h-80 overflow-y-auto pr-2">
                      {PROCESS_STEPS.map((step, index) => {
                        const isCompleted = currentStep > index + 1;
                        const isActive = currentStep === index + 1;
                        
                        return (
                          <div key={index} className={`rounded-lg p-3 ${isActive ? 'bg-primary/10 border border-primary/20' : ''}`}>
                            <div className="flex items-center gap-3">
                              <div className="flex-shrink-0">
                                {isCompleted ? (
                                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                                ) : isActive ? (
                                  <LoadingSpinner className="h-5 w-5" />
                                ) : (
                                  <Circle className="h-5 w-5 text-gray-300" />
                                )}
                              </div>
                              <div className="flex-grow">
                                <div className={`font-medium ${isActive ? 'text-primary' : isCompleted ? 'text-muted-foreground' : 'text-gray-400'}`}>
                                  {step.title}
                                  {isActive && <span className="animate-pulse">...</span>}
                                </div>
                                {(isActive || isCompleted) && (
                                  <div className={`text-xs mt-1 ${isActive ? 'text-primary/80' : 'text-muted-foreground'}`}>
                                    {step.description}
                                  </div>
                                )}
                              </div>
                              {(isCompleted || isActive) && (
                                <div className="w-20 text-right text-xs font-medium">
                                  <span className={isCompleted ? 'text-green-500' : 'text-primary'}>
                                    {isCompleted ? 'Completed' : 'In progress'}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    
                    <div className="text-center text-sm text-muted-foreground mt-4 bg-muted/50 p-3 rounded-lg">
                      <p>This might take a moment. We're using AI to analyze your resume against the job requirements.</p>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
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
                  Upload your resume and define job requirements to get started
                </CardDescription>
              </CardHeader>
              <CardContent className="min-h-[300px] flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <p>Your resume analysis results will appear here</p>
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
