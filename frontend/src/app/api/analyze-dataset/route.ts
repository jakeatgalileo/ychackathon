import { NextResponse } from 'next/server';

interface DatasetAnalysisRequest {
  datasetUrl: string;
  datasetName: string;
  owner: string;
  fileData: {
    filename: string;
    columns: string[];
    preview: Record<string, string>[];
  }[];
}

// Toggle this to enable actual MCP server calls
const USE_REAL_MCP_SERVER = true;
const MCP_SERVER_URL = 'http://localhost:8000/mcp';

export async function POST(request: Request) {
  try {
    const data: DatasetAnalysisRequest = await request.json();
    
    // Validate the request body
    if (!data.datasetUrl || !data.datasetName || !data.owner || !data.fileData) {
      return NextResponse.json(
        { error: 'Missing required dataset information' },
        { status: 400 }
      );
    }

    console.log(`Sending dataset ${data.datasetName} to MCP server for analysis`);
    
    let llmAnalysis;
    
    if (USE_REAL_MCP_SERVER) {
      // Real MCP server call
      try {
        // First, get dataset info resource
        const datasetInfoResponse = await fetch(`${MCP_SERVER_URL}/resources/dataset/${data.owner}/${data.datasetName}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        if (!datasetInfoResponse.ok) {
          throw new Error(`Failed to get dataset info: ${datasetInfoResponse.statusText}`);
        }
        
        const datasetInfo = await datasetInfoResponse.json();
        
        // Then, analyze the first file in the dataset
        const firstFile = data.fileData[0];
        if (firstFile) {
          const mlTaskResponse = await fetch(`${MCP_SERVER_URL}/tools/identify_ml_task`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              columns: firstFile.columns,
              sample_data: firstFile.preview
            }),
          });
          
          if (!mlTaskResponse.ok) {
            throw new Error(`Failed to identify ML task: ${mlTaskResponse.statusText}`);
          }
          
          const mlTaskResult = await mlTaskResponse.json();
          
          // Call add tool as a simple demo
          const addResponse = await fetch(`${MCP_SERVER_URL}/tools/add`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              a: 10,
              b: 20
            }),
          });
          
          const addResult = await addResponse.json();
          
          // Format the response to match our UI expectations
          llmAnalysis = {
            summary: `This dataset "${data.datasetName}" by ${data.owner} contains ${data.fileData.length} files. ` +
              `The main file appears to be ${firstFile.filename} with ${firstFile.columns.length} features. ` +
              `This dataset could be used for ${mlTaskResult.suggested_tasks.join(', ')}. ` +
              `${mlTaskResult.target_column ? `The target column appears to be '${mlTaskResult.target_column}'.` : 'No clear target column was identified.'}`,
            recommendations: [
              "Consider normalizing numeric columns for better model performance",
              `Analyze the '${mlTaskResult.target_column || 'target'}' column distribution`,
              "Check for missing values in the dataset"
            ],
            tools_used: [
              {
                name: "identify_ml_task",
                description: "Identifies potential machine learning tasks for a dataset",
                examples: mlTaskResult.suggested_tasks
              },
              {
                name: "add",
                description: "Simple mathematical operation",
                examples: [`10 + 20 = ${addResult}`]
              },
              {
                name: "dataset_resource",
                description: "Retrieves dataset metadata",
                examples: [datasetInfo.description]
              }
            ]
          };
        } else {
          throw new Error("No file data available to analyze");
        }
      } catch (error) {
        console.error("MCP server error:", error);
        // Fall back to mock data if MCP server call fails
        llmAnalysis = getMockAnalysis(data);
      }
    } else {
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Use mock data for demonstration
      llmAnalysis = getMockAnalysis(data);
    }
    
    return NextResponse.json({
      success: true,
      datasetUrl: data.datasetUrl,
      analysis: llmAnalysis
    });
    
  } catch (error) {
    console.error('Error analyzing dataset:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to analyze dataset' },
      { status: 500 }
    );
  }
}

// Helper function for mock LLM analysis
function getMockAnalysis(data: DatasetAnalysisRequest) {
  return {
    summary: `This dataset "${data.datasetName}" by ${data.owner} contains ${data.fileData.length} files. ` +
      `The main file appears to be ${data.fileData[0]?.filename || "unknown"} with ${data.fileData[0]?.columns.length || 0} features. ` +
      `This dataset could be used for ${data.fileData[0]?.columns.includes('target') ? 'classification' : 'various machine learning tasks'}.`,
    recommendations: [
      "Consider normalizing numeric columns for better model performance",
      "Check for missing values in the dataset",
      "Explore feature correlations to identify important predictors"
    ],
    tools_used: [
      {
        name: "add",
        description: "Used for calculating dataset statistics",
        examples: ["Computing mean values", "Aggregating counts"]
      },
      {
        name: "identify_ml_task",
        description: "Identifies potential machine learning tasks",
        examples: ["Classification", "Regression", "Clustering"]
      },
      {
        name: "analyze_dataset_columns",
        description: "Infers data types from dataset columns",
        examples: ["Identifying numeric features", "Detecting categorical variables"]
      }
    ]
  };
} 