# Import necessary libraries
from typing import Any
import httpx
from fastmcp import FastMCP
# from mcp.server.fastmcp import FastMCP, Context
import anthropic
import logging
import os
import pandas as pd
from dotenv import load_dotenv
from utils import load_data, dirtify

mcp = FastMCP("dataprep")

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Add StreamHandler to output logs to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Add this near the top of the file after imports
load_dotenv()  # This loads the .env file

# Initialize FastMCP server
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError('ANTHROPIC_API_KEY not found in environment variables or .env file')
logger.info('API key loaded successfully')
client = anthropic.Anthropic(
    api_key=api_key
)

# Initialize the dataset path
LATEST_DATASET_FPATH = "../yelp_dirty_data.csv"
CLEAN_DATASET_PREFIX = "../yelp_clean_data_v"

@mcp.resource(
    uri="data://dataset",
    description="Gets the dataset filepath",
    mime_type="text/plain",
)
def get_latest_dataset_filepath() -> str:
    # (maybe) FIXME point to the local path
    return LATEST_DATASET_FPATH

@mcp.tool()
def get_dataset_sample(sample_size: int = 10) -> str:
    df = load_data(LATEST_DATASET_FPATH)
    sample_rows = df.head(sample_size).to_dict('records')
    # Convert the sample rows to a formatted text string
    text_output = []
    for i, row in enumerate(sample_rows, 1):
        text_output.append(f"Row {i}:")
        for key, value in row.items():
            text_output.append(f"  {key}: {value}")
        text_output.append("")  # Add blank line between rows
    return "\n".join(text_output)

@mcp.prompt()
def analyze_dataset_schema_prompt(dataset_sample: str):
    """Generates a user message that analyzes and infers the dataset schema based on a sample"""
    return f"Based on the following sample rows for the dataset, please infer the column schema and start thinking of how to clean and validate the dataset '{dataset_sample}'?"

@mcp.tool()
def analyze_dataset_schema(dataset_sample: str) -> str:
    system_prompt = """You are a data analysis expert. Your task is to analyze dataset samples and provide:
1. A detailed column schema with inferred data types
2. A comprehensive list of data cleaning and validation tasks
Be specific and thorough in your analysis, focusing on data quality, consistency, and potential issues."""

    user_prompt = f"""Based on the following dataset sample, please provide:

1. A column-by-column schema analysis, including:
   - Column name
   - Inferred data type
   - Expected format/pattern (if applicable)
   - Potential data quality concerns

2. A detailed list of recommended data cleaning and validation tasks, such as:
   - Type validation and conversion
   - Missing value handling. Remove rows with missing values
   - Data consistency checks

Here's the dataset sample:
{dataset_sample}"""

    logger.info('sending dataset analysis to claude')
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=2000,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt},
        ]
    )
    logger.info(message.content[0].text)
    return message.content[0].text


# @mcp.resource(
#     uri="data://dataset_sample/{sample_size}",
#     description="Get a sample of the dataset to better understand the schema",
#     mime_type="text/plain",
# )


@mcp.tool()
def remove_rows_with_null():
    df = load_data(LATEST_DATASET_FPATH)
    # Get initial row count
    initial_count = len(df)
    
    # Remove rows with any null values
    df_clean = df.dropna()
    
    # Get number of rows removed
    rows_removed = initial_count - len(df_clean)
    
    # Log the results
    logger.info(f"Removed {rows_removed} rows containing null values")
    logger.info(f"Original row count: {initial_count}")
    logger.info(f"New row count: {len(df_clean)}")
    
    # Find the next version number
    version = 1
    while os.path.exists(f"{CLEAN_DATASET_PREFIX}{version}.csv"):
        version += 1
    
    # Save the cleaned DataFrame
    output_path = f"{CLEAN_DATASET_PREFIX}{version}.csv"
    df_clean.to_csv(output_path, index=False)
    logger.info(f"Saved cleaned dataset to {output_path}")
    
    return df_clean

if __name__ == "__main__":
    # Initialize and run the server

    # FIXME reenamble!!!!!!!!!!!
    mcp.run(transport='stdio')

    # dataset_sample = get_dataset_sample()
    # analysis = analyze_dataset_schema(dataset_sample)
    # remove_rows_with_null()
    

    
