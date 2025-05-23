
import { useState } from "react";
import { FileText, Upload, Check, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface ResumeUploaderProps {
  selectedFile: File | null;
  onFileChange: (file: File | null) => void;
}

export const ResumeUploader = ({ selectedFile, onFileChange }: ResumeUploaderProps) => {
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  // Maximum file size (5MB)
  const MAX_FILE_SIZE = 5 * 1024 * 1024;

  const validateFile = (file: File): boolean => {
    // Reset previous error
    setError(null);

    // Check file type
    const fileType = file.type;
    const validTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!validTypes.includes(fileType)) {
      setError("Please upload a PDF or Word document");
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF or Word document (.pdf, .doc, .docx)",
        variant: "destructive",
      });
      return false;
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      setError(`File size exceeds 5MB limit (${(file.size / (1024 * 1024)).toFixed(2)}MB)`);
      toast({
        title: "File too large",
        description: "Maximum file size is 5MB",
        variant: "destructive",
      });
      return false;
    }

    return true;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        onFileChange(file);
      } else {
        // Reset the file input
        e.target.value = '';
        onFileChange(null);
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        onFileChange(file);
      }
    }
  };

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium">Upload Resume</label>
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragging
            ? "border-primary bg-primary/5"
            : error
            ? "border-red-500 bg-red-50"
            : selectedFile
            ? "border-green-500 bg-green-50"
            : "border-gray-300 hover:border-primary"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          id="resume-upload"
          className="hidden"
          onChange={handleFileChange}
        />

        {error ? (
          <div className="flex flex-col items-center">
            <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center mb-3">
              <AlertCircle className="h-6 w-6 text-red-600" />
            </div>
            <p className="text-sm font-medium text-red-600">{error}</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-3"
              onClick={() => {
                setError(null);
                onFileChange(null);
              }}
            >
              Try Again
            </Button>
          </div>
        ) : selectedFile ? (
          <div className="flex flex-col items-center">
            <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center mb-3">
              <Check className="h-6 w-6 text-green-600" />
            </div>
            <p className="text-sm font-medium">{selectedFile.name}</p>
            <p className="text-xs text-gray-500 mt-1">
              {(selectedFile.size / 1024).toFixed(0)} KB
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-3"
              onClick={() => onFileChange(null)}
            >
              Change File
            </Button>
          </div>
        ) : (
          <label htmlFor="resume-upload" className="cursor-pointer">
            <div className="flex flex-col items-center">
              <div className="h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center mb-3">
                <Upload className="h-5 w-5 text-gray-600" />
              </div>
              <p className="text-sm font-medium">
                Drag and drop your resume or click to browse
              </p>
              <p className="text-xs text-gray-500 mt-1">
                PDF or Word files only (max 5MB)
              </p>
              <Button variant="secondary" size="sm" className="mt-3">
                <FileText className="mr-2 h-4 w-4" /> Select Resume
              </Button>
            </div>
          </label>
        )}
      </div>
    </div>
  );
};
