
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface ImprovedResumeProps {
  resumeText: string;
}

export const ImprovedResume = ({ resumeText }: ImprovedResumeProps) => {
  const { toast } = useToast();
  
  // Function to convert markdown to HTML (very basic)
  const markdownToHtml = (markdown: string) => {
    let html = markdown
      // Headers
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold my-4">$1</h1>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold my-3">$1</h2>')
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold my-2">$1</h3>')
      // Lists
      .replace(/^\- (.*$)/gm, '<li class="ml-4">$1</li>')
      // Bold
      .replace(/\*\*(.*)\*\*/gm, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*)\*/gm, '<em>$1</em>')
      // Paragraphs
      .split('\n\n').join('</p><p class="my-2">')
      
    return `<p class="my-2">${html}</p>`;
  };

  const copyResume = () => {
    navigator.clipboard.writeText(resumeText);
    toast({
      title: "Copied!",
      description: "Improved resume copied to clipboard"
    });
  };

  const downloadResume = () => {
    const element = document.createElement("a");
    const file = new Blob([resumeText], {type: "text/plain"});
    element.href = URL.createObjectURL(file);
    element.download = "improved_resume.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    toast({
      title: "Downloaded!",
      description: "Improved resume downloaded as text file"
    });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Improved Resume</CardTitle>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={copyResume}>
            Copy
          </Button>
          <Button size="sm" onClick={downloadResume}>
            Download
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
          <div 
            className="prose prose-sm max-w-none font-mono whitespace-pre-line" 
            dangerouslySetInnerHTML={{ __html: markdownToHtml(resumeText) }}
          />
        </div>
      </CardContent>
    </Card>
  );
};
