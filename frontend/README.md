# Data Analyzer Web App

This application provides two main features:
1. Web page analysis - analyze content and structure of web pages
2. Kaggle dataset downloading - fetch and preview datasets from Kaggle

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Kaggle account and API credentials (for dataset downloading)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
cd frontend
npm install
```

### Setting up Kaggle API credentials

To use the Kaggle dataset download feature, you need to set up your Kaggle API credentials:

1. Sign up for a Kaggle account if you don't have one already at [kaggle.com](https://www.kaggle.com)
2. Go to your account settings page (click on your profile picture → Account)
3. Scroll down to the "API" section and click "Create New API Token"
4. This will download a `kaggle.json` file containing your API credentials

Then, set up your credentials using ONE of the following methods:

#### Method 1: Create a .env.local file (recommended for development)

Create a `.env.local` file in the root of your project with the following content:

```
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

Replace `your_kaggle_username` and `your_kaggle_api_key` with the values from your `kaggle.json` file.

#### Method 2: Place kaggle.json in the .kaggle directory

On Unix-based systems (Linux/Mac):
```bash
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

On Windows:
```powershell
mkdir -f "$env:USERPROFILE\.kaggle"
copy kaggle.json "$env:USERPROFILE\.kaggle\"
```

### Running the application

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## Features

### URL Analyzer

Enter any URL to analyze its content structure. The analyzer will provide information about:
- Page title
- Number of headings
- Number of links
- Number of images
- Total word count
- Summary of the page content

### Dataset Downloader

Enter a Kaggle dataset URL (e.g., https://www.kaggle.com/datasets/owner/dataset-name) to:
- Download the dataset files
- See a preview of each tabular data file (CSV, TSV, etc.)
- Get a direct link to the dataset on Kaggle

## Development

The application is built with:
- Next.js 15+
- React
- TypeScript
- Tailwind CSS
- shadcn/ui components

### Project Structure

- `src/app/api/` - API routes
- `src/components/` - UI components
- `src/lib/` - Utility functions and hooks 