import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

type UserJob = {
  id: string;
  title: string;
  description: string;
  required_skills: string[];
  min_years_experience: number;
  min_education: string;
  created_at: string;
};

const JobRolesManager = ({ onSelectJob }: { onSelectJob: (jobId: string) => void }) => {
  const [activeTab, setActiveTab] = useState("browse");
  const [userJobs, setUserJobs] = useState<UserJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // New job form state
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [minYearsExperience, setMinYearsExperience] = useState(0);
  const [minEducation, setMinEducation] = useState("Bachelor's degree");

  // Load user's custom job roles on component mount
  useEffect(() => {
    fetchUserJobs();
  }, []);

  const fetchUserJobs = async () => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/user-jobs");
      if (response.ok) {
        const jobs = await response.json();
        setUserJobs(jobs);
      } else {
        console.error("Failed to fetch user jobs");
      }
    } catch (error) {
      console.error("Error fetching user jobs:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateJob = async () => {
    try {
      setIsLoading(true);
      // Convert comma-separated skills to array
      const skillsArray = requiredSkills.split(",").map(skill => skill.trim()).filter(Boolean);
      
      const response = await fetch("/api/user-jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: jobTitle,
          description: jobDescription,
          required_skills: skillsArray,
          min_years_experience: minYearsExperience,
          min_education: minEducation,
        }),
      });

      if (response.ok) {
        // Reset form
        setJobTitle("");
        setJobDescription("");
        setRequiredSkills("");
        setMinYearsExperience(0);
        setMinEducation("Bachelor's degree");
        
        // Refresh job list
        fetchUserJobs();
        
        // Switch to browse tab
        setActiveTab("browse");
      } else {
        console.error("Failed to create job");
      }
    } catch (error) {
      console.error("Error creating job:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/user-jobs/${jobId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        // Refresh job list
        fetchUserJobs();
      } else {
        console.error("Failed to delete job");
      }
    } catch (error) {
      console.error("Error deleting job:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Job Roles Manager</CardTitle>
        <CardDescription>
          Create and manage custom job roles to match with resumes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="w-full mb-6">
            <TabsTrigger value="browse" className="flex-1">Browse Job Roles</TabsTrigger>
            <TabsTrigger value="create" className="flex-1">Create New Job Role</TabsTrigger>
          </TabsList>
          
          <TabsContent value="browse">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Your Custom Job Roles</h3>
              
              {isLoading ? (
                <p>Loading job roles...</p>
              ) : userJobs.length === 0 ? (
                <p className="text-muted-foreground">
                  You haven't created any job roles yet. Switch to the "Create New" tab to get started.
                </p>
              ) : (
                <div className="space-y-4">
                  {userJobs.map((job) => (
                    <Card key={job.id} className="p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-bold">{job.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            Experience: {job.min_years_experience}+ years • Education: {job.min_education}
                          </p>
                          <p className="text-sm mt-2">{job.description.substring(0, 100)}...</p>
                          <div className="mt-2 flex flex-wrap gap-1">
                            {job.required_skills.map((skill, index) => (
                              <span 
                                key={index}
                                className="bg-primary/10 text-primary text-xs rounded-full px-2 py-0.5"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => onSelectJob(job.id)}
                          >
                            Select
                          </Button>
                          <Button 
                            variant="destructive" 
                            size="sm"
                            onClick={() => handleDeleteJob(job.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="create">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Create New Job Role</h3>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Job Title</Label>
                  <Input 
                    id="title" 
                    placeholder="e.g. Senior Software Engineer" 
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="description">Job Description</Label>
                  <Textarea 
                    id="description" 
                    placeholder="Enter detailed job description..." 
                    className="min-h-[100px]"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="skills">Required Skills (comma-separated)</Label>
                  <Input 
                    id="skills" 
                    placeholder="e.g. python, javascript, react" 
                    value={requiredSkills}
                    onChange={(e) => setRequiredSkills(e.target.value)}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="experience">Minimum Years Experience</Label>
                    <Input 
                      id="experience" 
                      type="number" 
                      min="0"
                      value={minYearsExperience}
                      onChange={(e) => setMinYearsExperience(parseInt(e.target.value))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="education">Minimum Education</Label>
                    <select
                      id="education"
                      className="w-full px-3 py-2 border rounded-md"
                      value={minEducation}
                      onChange={(e) => setMinEducation(e.target.value)}
                    >
                      <option value="High School">High School</option>
                      <option value="Associate's degree">Associate's Degree</option>
                      <option value="Bachelor's degree">Bachelor's Degree</option>
                      <option value="Master's degree">Master's Degree</option>
                      <option value="PhD">PhD</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter>
        {activeTab === "create" && (
          <Button 
            onClick={handleCreateJob} 
            className="w-full" 
            disabled={isLoading || !jobTitle || !jobDescription || !requiredSkills}
          >
            {isLoading ? "Creating..." : "Create Job Role"}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
};

export default JobRolesManager; 