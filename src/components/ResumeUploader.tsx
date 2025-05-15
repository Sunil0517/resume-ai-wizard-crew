
import { useState } from "react";
import { FileText, Upload, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ResumeUploaderProps {
  selectedFile: File | null;
  setSelectedFile: (file: File | null) => void;
}

export const ResumeUploader = ({ selectedFile, setSelectedFile }: ResumeUploaderProps) => {
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
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
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium">Upload Resume</label>
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragging
            ? "border-primary bg-primary/5"
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

        {selectedFile ? (
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
              onClick={() => setSelectedFile(null)}
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
