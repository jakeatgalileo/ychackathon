from sklearn.model_selection import train_test_split
from datasets import load_dataset
import logging
import pandas as pd
import numpy as np
import random

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

def create_and_save_dirty_dataset(filepath):
    train_data = load_data(filepath)
    dirty_df = dirtify(train_data, 0.01, 0.01)
    dirty_df.to_csv("dirty_data.csv", index=False)
