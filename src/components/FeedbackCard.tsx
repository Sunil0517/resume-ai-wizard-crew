
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface FeedbackCardProps {
  feedback: string;
}

export const FeedbackCard = ({ feedback }: FeedbackCardProps) => {
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

  const copyFeedback = () => {
    navigator.clipboard.writeText(feedback);
    toast({
      title: "Copied!",
      description: "Feedback copied to clipboard"
    });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Resume Feedback</CardTitle>
        <Button variant="outline" size="sm" onClick={copyFeedback}>
          Copy Feedback
        </Button>
      </CardHeader>
      <CardContent className="prose prose-sm max-w-none">
        <div dangerouslySetInnerHTML={{ __html: markdownToHtml(feedback) }} />
      </CardContent>
    </Card>
  );
};
