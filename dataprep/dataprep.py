# Import necessary libraries
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from datasets import load_dataset
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import random
import anthropic
import logging
import os
from dotenv import load_dotenv

# Initialize FastMCP server
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

def create_stratified_splits(df, total_size=0.005, test_fraction=0.1, val_fraction=0.2, random_state=42, stratify_col='label'):
    """
    Create stratified train, validation, and test splits from a DataFrame.
    
    Args:
        df: Input DataFrame
        total_size: Total fraction of data to use (default: 0.005)
        test_fraction: Fraction of total_size to use for test set (default: 0.2)
        val_fraction: Fraction of non-test data to use for validation (default: 0.2)
        random_state: Random seed for reproducibility (default: 42)
        stratify_col: Column to use for stratification (default: 'label')
    
    Returns:
        train_df, val_df, test_df: Tuple of DataFrames containing the splits
    """
    # Calculate sizes
    test_size = total_size * test_fraction
    train_val_size = total_size - test_size
    
    # First split: separate test set
    train_val_df, test_df = train_test_split(
        df,
        train_size=train_val_size,
        test_size=test_size,
        stratify=df[stratify_col],
        random_state=random_state
    )
    
    # Second split: separate train and validation
    train_df, val_df = train_test_split(
        train_val_df,
        train_size=(1 - val_fraction),  # e.g., 0.8 for val_fraction=0.2
        stratify=train_val_df[stratify_col],
        random_state=random_state
    )
    
    return train_df, val_df, test_df

def load_data(filepath):
    """
    Load data from a local CSV file into a pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame containing the loaded data
    """
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Successfully loaded data from {filepath}")
        logger.info(f"Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {str(e)}")
        return None

def dirtify(df, nullify_rate, malformat_rate):
    """
    Add noise to the DataFrame by introducing null values and malformed data.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        nullify_rate (float): Rate of null values to introduce (0-1)
        malformat_rate (float): Rate of malformed values to introduce in the 'star' column (0-1)
    
    Returns:
        pd.DataFrame: DataFrame with introduced noise
    """
    # Create a copy to avoid modifying the original DataFrame
    dirty_df = df.copy()
    
    # Introduce null values across all columns
    rows, cols = dirty_df.shape
    null_mask = np.random.random(size=(rows, cols)) < nullify_rate
    num_nullified = null_mask.sum()
    dirty_df[null_mask] = np.nan
    logger.info(f"Introduced {num_nullified} null values across {cols} columns")
    
    # Introduce malformed data in the 'star' column
    if 'label' not in dirty_df.columns:
        logger.error("DataFrame must contain a 'label' column for dirtification")
        raise ValueError("DataFrame must contain a 'label' column for dirtification")

    num_malformat = int(rows * malformat_rate)
    malformat_indices = random.sample(range(rows), num_malformat)
    
    # List of possible malformed values
    malformed_values = ['five stars', 'excellent', 'bad', '3.5', 'unknown', 'N/A']
    
    for idx in malformat_indices:
        dirty_df.loc[idx, 'label'] = random.choice(malformed_values)
    logger.info(f"Introduced {num_malformat} malformed values in the 'star' column")
    
    return dirty_df

def analyze_data_health(df):
    """
    Analyze the health of the DataFrame by checking for null values and type inconsistencies.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        
    Returns:
        dict: Dictionary containing analysis results
    """
    # Initialize results dictionary
    health_report = {
        'null_analysis': {},
        'type_analysis': {},
        'value_distribution': {}
    }
    
    # Analyze null values
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / len(df)) * 100
    health_report['null_analysis'] = {
        'total_null_count': null_counts.sum(),
        'null_counts_by_column': null_counts.to_dict(),
        'null_percentages': null_percentages.to_dict()
    }
    
    # Analyze data types and potential inconsistencies
    for column in df.columns:
        # Get the primary data type
        primary_type = df[column].dtype
        
        # Check for mixed types (excluding null values)
        non_null_values = df[column].dropna()
        unique_types = set(map(type, non_null_values))
        
        # Analyze unique values and their types
        unique_values = df[column].unique()
        value_types = {str(val): str(type(val)) for val in unique_values[:10]}  # First 10 unique values
        
        health_report['type_analysis'][column] = {
            'primary_dtype': str(primary_type),
            'unique_types': [str(t) for t in unique_types],
            'is_mixed_type': len(unique_types) > 1,
            'sample_value_types': value_types
        }
        
        # Add value distribution for categorical or small cardinality columns
        if primary_type == 'object' or (len(unique_values) < 10):
            value_counts = df[column].value_counts().head(10).to_dict()
            health_report['value_distribution'][column] = value_counts
    
    # Print summary report
    logger.info("\n=== Data Health Analysis Report ===")
    logger.info(f"\nTotal rows: {len(df)}")
    logger.info(f"Total columns: {len(df.columns)}")
    logger.info("\nNull Value Summary:")
    for col, null_count in health_report['null_analysis']['null_counts_by_column'].items():
        if null_count > 0:
            percentage = health_report['null_analysis']['null_percentages'][col]
            logger.info(f"- {col}: {null_count} nulls ({percentage:.2f}%)")
    
    logger.info("\nType Inconsistencies:")
    for col, type_info in health_report['type_analysis'].items():
        if type_info['is_mixed_type']:
            logger.info(f"\n- {col}:")
            logger.info(f"  Primary dtype: {type_info['primary_dtype']}")
            logger.info(f"  Found types: {', '.join(type_info['unique_types'])}")
            logger.info("  Sample values and their types:")
            for val, val_type in type_info['sample_value_types'].items():
                logger.info(f"    {val}: {val_type}")
    
    return health_report

def get_dataset_snapshot(df, sample_size=10):
    """
    Get a representative snapshot of the dataset to help understand its schema and contents.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        sample_size (int): Number of sample rows to include (default: 5)
        include_stats (bool): Whether to include basic statistics (default: True)
        
    Returns:
        dict: Dictionary containing dataset snapshot information
    """
    sample_rows = df.head(sample_size).to_dict('records')
    

def create_new_splits(save_files=True):
    """
    Create new dataset splits from the Yelp Review Full dataset.
    
    Args:
        save_files: Boolean indicating whether to save the splits to CSV files (default: True)
        
    Returns:
        tuple: (train_df, val_df, test_df) DataFrames containing the splits
    """
    # Load the dataset using datasets library
    dataset = load_dataset("yelp_review_full")
    df = dataset["train"].to_pandas()

    # Create the splits
    train_df, val_df, test_df = create_stratified_splits(df)

    # Verify the distribution
    logger.info("Original distribution of stars:")
    logger.info(df['label'].value_counts(normalize=True))
    logger.info("\nTrain distribution of stars:")
    logger.info(train_df['label'].value_counts())
    logger.info("\nValidation distribution of stars:")
    logger.info(val_df['label'].value_counts())
    logger.info("\nTest distribution of stars:")
    logger.info(test_df['label'].value_counts())

    if save_files:
        # Save the split datasets
        train_df.to_csv('yelp_reviews_train.csv', index=False)
        val_df.to_csv('yelp_reviews_val.csv', index=False)
        test_df.to_csv('yelp_reviews_test.csv', index=False)
        logger.info("\nSplit datasets saved to CSV files.")

    return train_df, val_df, test_df

def test_anthropic():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError('ANTHROPIC_API_KEY not found in environment variables or .env file')
    logger.info('API key loaded successfully')

    client = anthropic.Anthropic(
        api_key=api_key
    )

    logger.info('sending hello message to claude')
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello, Claude"}
        ]
    )
    logger.info(message.content)


if __name__ == "__main__":
    train_data = load_data("../yelp_reviews_train.csv")
    dirty_df = dirtify(train_data, 0.01, 0.01)
    analyze_data_health(dirty_df)
    logger.info(train_data)

    # Initialize and run the server
    mcp.run(transport='stdio')