import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { url } = await request.json();
    
    if (!url || typeof url !== 'string') {
      return NextResponse.json(
        { error: 'URL is required and must be a string' },
        { status: 400 }
      );
    }

    if (!url.match(/^(https?:\/\/)/i)) {
      return NextResponse.json(
        { error: 'Please enter a valid URL starting with http:// or https://' },
        { status: 400 }
      );
    }

    // In a real implementation, this would call your MCP server
    // For now, we'll return mock data
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return NextResponse.json({
      success: true,
      url,
      analysis: {
        title: "Example Page Title",
        headings: 5,
        links: 12,
        images: 3,
        wordCount: 547,
        summary: "This is a mock summary of the analyzed webpage content."
      }
    });
  } catch (error) {
    console.error('Error analyzing URL:', error);
    return NextResponse.json(
      { error: 'Failed to analyze URL' },
      { status: 500 }
    );
  }
} 