
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface ScoreProps {
  score: {
    overall_score: number;
    skill_match_score: number;
    experience_score: number;
    education_score: number;
    matching_skills: string[];
    missing_skills: string[];
  };
}

export const ResumeScore = ({ score }: ScoreProps) => {
  // Helper to determine score color
  const getScoreColor = (value: number) => {
    if (value >= 0.8) return "bg-green-500";
    if (value >= 0.6) return "bg-yellow-500";
    return "bg-red-500";
  };

  // Helper to determine score text
  const getScoreText = (value: number) => {
    if (value >= 0.8) return "Excellent";
    if (value >= 0.6) return "Good";
    if (value >= 0.4) return "Fair";
    return "Poor";
  };

  return (
    <Card className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div className="w-full md:w-1/3">
          <div className="text-center">
            <div className="text-sm text-muted-foreground mb-2">Overall Match</div>
            <div className="relative w-36 h-36 mx-auto">
              <div className="absolute inset-0 rounded-full border-8 border-gray-100"></div>
              <div 
                className="absolute inset-0 rounded-full border-8 border-transparent"
                style={{ 
                  clipPath: `polygon(50% 50%, 50% 0%, ${50 + 50 * Math.sin(2 * Math.PI * score.overall_score)}% ${50 - 50 * Math.cos(2 * Math.PI * score.overall_score)}%)`,
                  borderColor: getScoreColor(score.overall_score)
                }}
              ></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div>
                  <div className="text-4xl font-bold">
                    {Math.round(score.overall_score * 100)}%
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {getScoreText(score.overall_score)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="w-full md:w-2/3 space-y-4">
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">Skills Match</span>
              <span className={`text-sm font-medium ${getScoreColor(score.skill_match_score).replace('bg-', 'text-')}`}>
                {Math.round(score.skill_match_score * 100)}%
              </span>
            </div>
            <Progress value={score.skill_match_score * 100} className={`h-2 ${getScoreColor(score.skill_match_score)}`} />
          </div>
          
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">Experience</span>
              <span className={`text-sm font-medium ${getScoreColor(score.experience_score).replace('bg-', 'text-')}`}>
                {Math.round(score.experience_score * 100)}%
              </span>
            </div>
            <Progress value={score.experience_score * 100} className={`h-2 ${getScoreColor(score.experience_score)}`} />
          </div>
          
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">Education</span>
              <span className={`text-sm font-medium ${getScoreColor(score.education_score).replace('bg-', 'text-')}`}>
                {Math.round(score.education_score * 100)}%
              </span>
            </div>
            <Progress value={score.education_score * 100} className={`h-2 ${getScoreColor(score.education_score)}`} />
          </div>
          
          <div className="pt-2 flex flex-wrap gap-2">
            {score.matching_skills.map((skill) => (
              <span key={skill} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                {skill}
              </span>
            ))}
            {score.missing_skills.map((skill) => (
              <span key={skill} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};
