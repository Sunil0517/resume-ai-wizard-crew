import { useState, useEffect } from "react";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";

interface CustomJobFormProps {
  onSubmitCustomJob: (jobDetails: {
    title: string;
    description: string;
    requiredSkills: string[];
    minYearsExperience: number;
    minEducation: string;
  }) => void;
}

const JobRolesManager = ({ onSubmitCustomJob }: CustomJobFormProps) => {
  // Form state
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [minYearsExperience, setMinYearsExperience] = useState(0);
  const [minEducation, setMinEducation] = useState("Bachelor's degree");
  const [formFilled, setFormFilled] = useState(false);

  // Automatically update the job requirements whenever inputs change
  useEffect(() => {
    if (jobTitle && requiredSkills) {
      setFormFilled(true);
      updateJobRequirements();
    } else {
      setFormFilled(false);
    }
  }, [jobTitle, jobDescription, requiredSkills, minYearsExperience, minEducation]);

  const updateJobRequirements = () => {
    // Convert comma-separated skills to array
    const skillsArray = requiredSkills.split(",").map(skill => skill.trim()).filter(Boolean);
    
    // Submit the job details
    onSubmitCustomJob({
      title: jobTitle,
      description: jobDescription,
      requiredSkills: skillsArray,
      minYearsExperience: minYearsExperience,
      minEducation: minEducation
    });
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="title">Job Title*</Label>
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
          placeholder="Enter job description..." 
          className="min-h-[80px]"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="skills">Required Skills (comma-separated)*</Label>
        <Input 
          id="skills" 
          placeholder="e.g. python, javascript, react" 
          value={requiredSkills}
          onChange={(e) => setRequiredSkills(e.target.value)}
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="experience">Min. Years Experience</Label>
          <Input 
            id="experience" 
            type="number" 
            min="0"
            value={minYearsExperience}
            onChange={(e) => setMinYearsExperience(parseInt(e.target.value))}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="education">Min. Education</Label>
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
      <p className="text-sm text-muted-foreground">* Required fields</p>
    </div>
  );
};

export default JobRolesManager; 