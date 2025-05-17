import { NextResponse } from 'next/server';
import { parseKaggleDatasetUrl } from '@/lib/kaggle-utils';

// Mock data for dataset preview
const mockDatasetPreviews = [
  {
    filename: 'train.csv',
    columns: ['id', 'name', 'age', 'gender', 'score'],
    preview: [
      { id: '1', name: 'John Doe', age: '32', gender: 'Male', score: '85.4' },
      { id: '2', name: 'Jane Smith', age: '28', gender: 'Female', score: '92.1' },
      { id: '3', name: 'Bob Johnson', age: '45', gender: 'Male', score: '78.9' },
      { id: '4', name: 'Alice Brown', age: '35', gender: 'Female', score: '89.7' },
      { id: '5', name: 'Charlie Davis', age: '29', gender: 'Male', score: '76.2' }
    ]
  },
  {
    filename: 'test.csv',
    columns: ['id', 'name', 'age', 'gender'],
    preview: [
      { id: '101', name: 'Eva Wilson', age: '31', gender: 'Female' },
      { id: '102', name: 'Frank Miller', age: '42', gender: 'Male' },
      { id: '103', name: 'Grace Lee', age: '27', gender: 'Female' }
    ]
  }
];

// Mock data for competition preview
const mockCompetitionPreviews = [
  {
    filename: 'sample_submission.csv',
    columns: ['id', 'prediction'],
    preview: [
      { id: '0', prediction: '0' },
      { id: '1', prediction: '1' },
      { id: '2', prediction: '0' },
      { id: '3', prediction: '1' },
      { id: '4', prediction: '0' }
    ]
  },
  {
    filename: 'train.csv',
    columns: ['id', 'feature1', 'feature2', 'feature3', 'target'],
    preview: [
      { id: '1', feature1: '23.5', feature2: '45.2', feature3: '12.1', target: '0' },
      { id: '2', feature1: '18.7', feature2: '32.6', feature3: '9.4', target: '1' },
      { id: '3', feature1: '27.3', feature2: '41.8', feature3: '15.7', target: '0' },
      { id: '4', feature1: '22.1', feature2: '38.9', feature3: '11.3', target: '1' }
    ]
  },
  {
    filename: 'test.csv',
    columns: ['id', 'feature1', 'feature2', 'feature3'],
    preview: [
      { id: '101', feature1: '24.8', feature2: '43.6', feature3: '13.2' },
      { id: '102', feature1: '19.3', feature2: '35.1', feature3: '10.5' },
      { id: '103', feature1: '28.9', feature2: '44.2', feature3: '16.8' }
    ]
  }
];

export async function POST(request: Request) {
  try {
    const { url } = await request.json();
    
    if (!url || typeof url !== 'string') {
      return NextResponse.json(
        { error: 'URL is required and must be a string' },
        { status: 400 }
      );
    }

    // Check if it's a Kaggle dataset URL
    const datasetInfo = parseKaggleDatasetUrl(url);
    if (!datasetInfo) {
      return NextResponse.json(
        { error: 'Not a valid Kaggle URL. Please provide a URL like https://www.kaggle.com/datasets/owner/dataset-name or https://www.kaggle.com/competitions/competition-name' },
        { status: 400 }
      );
    }

    await new Promise(resolve => setTimeout(resolve, 2000));

    const mockPreviews = datasetInfo.type === 'dataset' ? 
      mockDatasetPreviews : 
      mockCompetitionPreviews;
    
    return NextResponse.json({
      success: true,
      dataset: {
        owner: datasetInfo.owner,
        name: datasetInfo.dataset,
        url: url,
        previews: mockPreviews
      }
    });
    
  } catch (error) {
    console.error('Error processing dataset:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to process dataset' },
      { status: 500 }
    );
  }
} 