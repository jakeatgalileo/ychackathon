"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

// Enhanced loading spinner component
function LoadingSpinner({ className = "h-5 w-5", textColor = "text-white" }: { className?: string, textColor?: string }) {
  return (
    <div className="flex items-center gap-2">
      <svg 
        className={`animate-spin ${className}`} 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          className="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="4"
        ></circle>
        <path 
          className="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <span className={textColor}>Downloading...</span>
    </div>
  );
}

// Analysis result type
type AnalysisResult = {
  title: string;
  headings: number;
  links: number;
  images: number;
  wordCount: number;
  summary: string;
};

// Dataset preview type
type DatasetPreview = {
  filename: string;
  columns: string[];
  preview: Record<string, string>[];
};

// Dataset result type
type DatasetResult = {
  owner: string;
  name: string;
  url: string;
  previews: DatasetPreview[];
};

// LLM Analysis result type
type LlmAnalysis = {
  summary: string;
  recommendations: string[];
  tools_used: {
    name: string;
    description: string;
    examples: string[];
  }[];
};

export function MleAgentComponent() {
  const [url, setUrl] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [datasetResult, setDatasetResult] = useState<DatasetResult | null>(null);
  const [llmAnalysis, setLlmAnalysis] = useState<LlmAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDataset, setIsDataset] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Function to check if a URL is a Kaggle dataset or competition URL
  const isKaggleDatasetUrl = (url: string): boolean => {
    // Match both dataset and competition URLs
    return /kaggle\.com\/(?:(?:datasets|competitions)\/)?([^\/]+)\/([^\/]+)/i.test(url);
  };

  const analyzeDatasetWithLLM = async (dataset: DatasetResult) => {
    setIsAnalyzing(true);
    setLlmAnalysis(null);
    
    try {
      const response = await fetch('/api/analyze-dataset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          datasetUrl: dataset.url,
          datasetName: dataset.name,
          owner: dataset.owner,
          fileData: dataset.previews
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze dataset with LLM');
      }
      
      setLlmAnalysis(data.analysis);
      
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to analyze dataset with LLM");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async () => {
    if (!url.trim()) return;
    
    setIsProcessing(true);
    setAnalysisResult(null);
    setDatasetResult(null);
    setLlmAnalysis(null);
    setError(null);
    setDownloadProgress(0);
    
    try {
      // Check if URL is a Kaggle dataset
      const isKaggle = isKaggleDatasetUrl(url);
      setIsDataset(isKaggle);
      
      if (isKaggle) {
        // For Kaggle URLs, simulate download progress
        const progressInterval = setInterval(() => {
          setDownloadProgress(prev => {
            const newProgress = prev + Math.random() * 15;
            return newProgress >= 100 ? 100 : newProgress;
          });
        }, 200);
        
        // Process as dataset
        const response = await fetch('/api/download-dataset', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url }),
        });
        
        clearInterval(progressInterval);
        setDownloadProgress(100);
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to process dataset');
        }
        
        setDatasetResult(data.dataset);
        
        // Automatically analyze the dataset with LLM after downloading
        if (data.dataset) {
          await analyzeDatasetWithLLM(data.dataset);
        }
      } else {
        // Process as regular URL for analysis
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to analyze URL');
        }
        
        setAnalysisResult(data.analysis);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "An unknown error occurred");
    } finally {
      setIsProcessing(false);
    }
  };

  // Component to render a data table preview
  const DataTable = ({ filename, columns, preview }: DatasetPreview) => {
    return (
      <div className="overflow-x-auto mt-4 mb-6">
        <h4 className="font-medium text-sm mb-2">{filename}</h4>
        <table className="min-w-full border border-border text-sm">
          <thead>
            <tr className="bg-muted">
              {columns.map((column, i) => (
                <th key={i} className="py-2 px-3 text-left border-b border-border">{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? "bg-background" : "bg-muted/20"}>
                {columns.map((column, j) => (
                  <td key={j} className="py-2 px-3 border-b border-border">{row[column] || ''}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <Card className="w-full shadow-md">
        <CardHeader className="bg-card">
          <CardTitle>Data Analyzer</CardTitle>
          <CardDescription>
            Enter a URL to analyze its content or download Kaggle datasets
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div>
              <Textarea
                placeholder="Paste URL here (e.g., https://example.com or https://www.kaggle.com/datasets/owner/dataset-name)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="min-h-[100px] w-full resize-none"
                disabled={isProcessing}
              />
            </div>
            
            {error && (
              <div className="bg-destructive/10 text-destructive-foreground p-4 rounded-md border border-destructive/30">
                <h3 className="font-medium mb-1">Error:</h3>
                <p>{error}</p>
              </div>
            )}
            
            {/* Show download progress for Kaggle URLs */}
            {isProcessing && isDataset && (
              <div className="mt-4">
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-300 ease-out"
                    style={{ width: `${downloadProgress}%` }}
                  ></div>
                </div>
                <p className="text-xs mt-1 text-muted-foreground">
                  Downloading... {Math.round(downloadProgress)}%
                </p>
              </div>
            )}
            
            {/* Display LLM analysis */}
            {llmAnalysis && (
              <div className="bg-primary/10 p-4 rounded-md border border-primary/30 mb-6">
                <h3 className="font-medium text-lg mb-2">LLM Analysis</h3>
                <div className="space-y-3">
                  <p className="text-sm">{llmAnalysis.summary}</p>
                  
                  {llmAnalysis.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-1">Recommendations:</h4>
                      <ul className="text-sm list-disc pl-5 space-y-1">
                        {llmAnalysis.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {llmAnalysis.tools_used.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-1">Tools Used by MCP Server:</h4>
                      <div className="grid gap-2 mt-2">
                        {llmAnalysis.tools_used.map((tool, i) => (
                          <div key={i} className="bg-muted p-2 rounded border border-border">
                            <div className="font-medium">{tool.name}</div>
                            <div className="text-xs text-muted-foreground mt-1">{tool.description}</div>
                            {tool.examples.length > 0 && (
                              <div className="text-xs mt-1">
                                <span className="opacity-70">Examples:</span> {tool.examples.join(", ")}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Display dataset preview */}
            {datasetResult && (
              <div className="bg-muted/50 p-4 rounded-md border border-border">
                <h3 className="font-medium text-lg mb-2">Dataset: {datasetResult.owner}/{datasetResult.name}</h3>
                
                <div className="mb-4">
                  <p className="text-sm mb-2">
                    This dataset contains {datasetResult.previews.length} files. 
                    Here's a preview of each:
                  </p>
                </div>
                
                {datasetResult.previews.map((preview, index) => (
                  <DataTable 
                    key={index}
                    filename={preview.filename}
                    columns={preview.columns}
                    preview={preview.preview}
                  />
                ))}
                
                <div className="mt-4 flex justify-between items-center">
                  <a 
                    href={datasetResult.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:text-primary/80 text-sm underline"
                  >
                    View full dataset on Kaggle →
                  </a>
                  
                  {!llmAnalysis && !isAnalyzing && (
                    <Button
                      onClick={() => analyzeDatasetWithLLM(datasetResult)}
                      size="sm"
                      variant="outline"
                    >
                      Analyze with LLM
                    </Button>
                  )}
                  
                  {isAnalyzing && (
                    <div className="text-sm text-muted-foreground flex items-center">
                      <svg 
                        className="animate-spin h-4 w-4 mr-2" 
                        xmlns="http://www.w3.org/2000/svg" 
                        fill="none" 
                        viewBox="0 0 24 24"
                      >
                        <circle 
                          className="opacity-25" 
                          cx="12" 
                          cy="12" 
                          r="10" 
                          stroke="currentColor" 
                          strokeWidth="4"
                        ></circle>
                        <path 
                          className="opacity-75" 
                          fill="currentColor" 
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Analyzing with LLM...
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Display web analysis result */}
            {analysisResult && (
              <div className="bg-muted/50 p-4 rounded-md border border-border">
                <h3 className="font-medium mb-2 text-lg">Analysis Result:</h3>
                <div className="space-y-3">
                  <p><span className="font-medium">Page Title:</span> {analysisResult.title}</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-background p-2 rounded border border-border">
                      <span className="font-medium">Headings:</span> {analysisResult.headings}
                    </div>
                    <div className="bg-background p-2 rounded border border-border">
                      <span className="font-medium">Links:</span> {analysisResult.links}
                    </div>
                    <div className="bg-background p-2 rounded border border-border">
                      <span className="font-medium">Images:</span> {analysisResult.images}
                    </div>
                    <div className="bg-background p-2 rounded border border-border">
                      <span className="font-medium">Words:</span> {analysisResult.wordCount}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-1">Summary:</h4>
                    <p className="text-sm">{analysisResult.summary}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex items-center justify-end bg-card border-t border-border py-2">
          <Button 
            onClick={handleSubmit}
            disabled={!url.trim() || isProcessing}
            className="flex items-center gap-2 px-8 py-5 text-base font-medium"
            size="lg"
          >
            {isProcessing ? (
              isDataset ? <LoadingSpinner /> : "Analyzing..."
            ) : (
              isKaggleDatasetUrl(url) ? "Download & Preview" : "Analyze"
            )}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
