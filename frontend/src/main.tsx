import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Loader2, Send, Mic, FileText, AlertCircle, CheckCircle } from "lucide-react";

interface ProcessResponse {
  patient_info: {
    name: string;
    age: number;
    id?: string;
  };
  symptoms: string[];
  motive: string;
  diagnosis: string;
  treatment: string;
  recommendations: string;
  metadata: {
    request_id: string;
    model_version: string;
    prompt_version: string;
    latency_ms: number;
    timestamp: string;
    input_type: string;
  };
}

export default function Container(): JSX.Element {
  const [audioUrl, setAudioUrl] = useState("");
  const [userInput, setUserInput] = useState("");
  const [model, setModel] = useState("gpt-4");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState("");

  const handleProcess = async () => {
    if (!audioUrl && !userInput.trim()) {
      setError("Please provide either an audio URL or text input");
      return;
    }

    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/v1/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          audio_url: audioUrl || undefined,
          text: userInput || undefined,
          model: model,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ProcessResponse = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Doctor Assistant</h1>
          <p className="text-gray-600">Medical consultation powered by AI</p>
        </div>

        {/* Input Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Patient Information Input
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Model Selection */}
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium">AI Model:</label>
              <Select value={model} onValueChange={setModel}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gemini">Gemini</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Audio URL Input */}
            <div>
              <label className="text-sm font-medium mb-2 block">Audio File URL (Optional)</label>
              <Input
                placeholder="https://example.com/audio.mp3"
                value={audioUrl}
                onChange={(e) => setAudioUrl(e.target.value)}
                className="w-full"
              />
            </div>

            {/* Text Input */}
            <div>
              <label className="text-sm font-medium mb-2 block">Medical Description</label>
              <Textarea
                placeholder="Describe the patient's symptoms, medical history, or reason for visit..."
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                className="w-full min-h-[120px]"
                maxLength={1000}
              />
              <div className="text-xs text-gray-500 mt-1">
                {userInput.length}/1000 characters
              </div>
            </div>

            {/* Submit Button */}
            <Button 
              onClick={handleProcess} 
              disabled={isLoading || (!audioUrl && !userInput.trim())}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Analyze Medical Information
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle className="w-5 h-5" />
                <span className="font-medium">Error:</span>
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Display */}
        {result && (
          <div className="space-y-6">
            {/* Patient Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Patient Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Name</label>
                    <p className="text-lg font-semibold">{result.patient_info.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Age</label>
                    <p className="text-lg font-semibold">{result.patient_info.age}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Patient ID</label>
                    <p className="text-lg font-semibold">{result.patient_info.id || "Not provided"}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Symptoms */}
            <Card>
              <CardHeader>
                <CardTitle>Identified Symptoms</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {result.symptoms.map((symptom, index) => (
                    <Badge key={index} variant="secondary" className="text-sm">
                      {symptom}
                    </Badge>
                  ))}
                </div>
                <div className="mt-4">
                  <label className="text-sm font-medium text-gray-600">Reason for Visit</label>
                  <p className="text-gray-800 mt-1">{result.motive}</p>
                </div>
              </CardContent>
            </Card>

            {/* Medical Assessment */}
            <Card>
              <CardHeader>
                <CardTitle>Medical Assessment</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Diagnosis</label>
                  <p className="text-gray-800 mt-1 bg-blue-50 p-3 rounded-lg">{result.diagnosis}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Treatment Plan</label>
                  <p className="text-gray-800 mt-1 bg-green-50 p-3 rounded-lg">{result.treatment}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Recommendations</label>
                  <p className="text-gray-800 mt-1 bg-yellow-50 p-3 rounded-lg">{result.recommendations}</p>
                </div>
              </CardContent>
            </Card>

            {/* Metadata */}
            <Card>
              <CardHeader>
                <CardTitle>Analysis Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <label className="text-gray-600">Model Used</label>
                    <p className="font-medium">{result.metadata.model_version}</p>
                  </div>
                  <div>
                    <label className="text-gray-600">Processing Time</label>
                    <p className="font-medium">{result.metadata.latency_ms}ms</p>
                  </div>
                  <div>
                    <label className="text-gray-600">Input Type</label>
                    <p className="font-medium capitalize">{result.metadata.input_type}</p>
                  </div>
                  <div>
                    <label className="text-gray-600">Request ID</label>
                    <p className="font-medium font-mono text-xs">{result.metadata.request_id}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* HIPAA Notice */}
        <Card className="mt-8 border-orange-200 bg-orange-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
              <div>
                <p className="text-sm text-orange-800 font-medium">HIPAA Compliance Notice</p>
                <p className="text-xs text-orange-700 mt-1">
                  This AI assistant is for informational purposes only and should not replace professional medical advice. 
                  All patient data is processed securely and in compliance with healthcare privacy regulations.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 