import { SelectValue, SelectTrigger, SelectItem, SelectContent, Select } from "@/components/ui/select";

interface JobSelectorProps {
  selectedJob: string;
  onJobChange: (jobId: string) => void;
}

export const JobSelector = ({ selectedJob, onJobChange }: JobSelectorProps) => {
  const jobs = [
    { id: "job1", title: "Senior Software Engineer" },
    { id: "job2", title: "Data Scientist" },
    { id: "job3", title: "Product Manager" }
  ];

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium">Select Job Position</label>
      <Select value={selectedJob} onValueChange={onJobChange}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select a job position" />
        </SelectTrigger>
        <SelectContent>
          {jobs.map(job => (
            <SelectItem key={job.id} value={job.id}>{job.title}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <p className="text-xs text-muted-foreground">
        The selected job will be used to analyze how well your resume matches the requirements.
      </p>
    </div>
  );
};
