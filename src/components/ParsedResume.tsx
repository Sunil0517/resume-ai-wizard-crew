
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface ParsedResumeProps {
  resume: {
    name: string;
    contact_info: {
      email: string;
      phone: string;
      linkedin: string;
      location: string;
    };
    education: Array<{
      degree: string;
      institution: string;
      date_range: string;
      field_of_study: string;
    }>;
    skills: string[];
    experience: Array<{
      title: string;
      company: string;
      date_range: string;
      description: string;
    }>;
  };
}

export const ParsedResume = ({ resume }: ParsedResumeProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Parsed Resume Data</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="contact" className="w-full">
          <TabsList className="grid grid-cols-4 mb-4">
            <TabsTrigger value="contact">Contact</TabsTrigger>
            <TabsTrigger value="experience">Experience</TabsTrigger>
            <TabsTrigger value="education">Education</TabsTrigger>
            <TabsTrigger value="skills">Skills</TabsTrigger>
          </TabsList>
          
          <TabsContent value="contact">
            <div className="space-y-3">
              <div>
                <h3 className="font-semibold">Name</h3>
                <p>{resume.name}</p>
              </div>
              {resume.contact_info.email && (
                <div>
                  <h3 className="font-semibold">Email</h3>
                  <p>{resume.contact_info.email}</p>
                </div>
              )}
              {resume.contact_info.phone && (
                <div>
                  <h3 className="font-semibold">Phone</h3>
                  <p>{resume.contact_info.phone}</p>
                </div>
              )}
              {resume.contact_info.linkedin && (
                <div>
                  <h3 className="font-semibold">LinkedIn</h3>
                  <p>{resume.contact_info.linkedin}</p>
                </div>
              )}
              {resume.contact_info.location && (
                <div>
                  <h3 className="font-semibold">Location</h3>
                  <p>{resume.contact_info.location}</p>
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="experience">
            {resume.experience.length > 0 ? (
              <div className="space-y-6">
                {resume.experience.map((job, index) => (
                  <div key={index} className="space-y-2 border-b pb-4 last:border-0">
                    <h3 className="font-semibold">{job.title}</h3>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{job.company}</span>
                      <span className="text-muted-foreground">{job.date_range}</span>
                    </div>
                    <p className="whitespace-pre-line text-sm">{job.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No experience data found</p>
            )}
          </TabsContent>
          
          <TabsContent value="education">
            {resume.education.length > 0 ? (
              <div className="space-y-4">
                {resume.education.map((edu, index) => (
                  <div key={index} className="space-y-1">
                    <h3 className="font-semibold">{edu.degree}</h3>
                    <p>{edu.institution}</p>
                    {edu.date_range && (
                      <p className="text-sm text-muted-foreground">{edu.date_range}</p>
                    )}
                    {edu.field_of_study && (
                      <p className="text-sm">{edu.field_of_study}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No education data found</p>
            )}
          </TabsContent>
          
          <TabsContent value="skills">
            {resume.skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {resume.skills.map((skill, index) => (
                  <span 
                    key={index} 
                    className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No skills data found</p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
