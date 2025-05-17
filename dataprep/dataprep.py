# Import necessary libraries
from datasets import load_dataset
from sklearn.model_selection import train_test_split
import pandas as pd

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
        print(f"Successfully loaded data from {filepath}")
        print(f"Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading data from {filepath}: {str(e)}")
        return None

def dirtify(df, nullify_rate, malformat_rate):
    pass

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
    print("Original distribution of stars:")
    print(df['label'].value_counts(normalize=True))
    print("\nTrain distribution of stars:")
    print(train_df['label'].value_counts())
    print("\nValidation distribution of stars:")
    print(val_df['label'].value_counts())
    print("\nTest distribution of stars:")
    print(test_df['label'].value_counts())

    if save_files:
        # Save the split datasets
        train_df.to_csv('yelp_reviews_train.csv', index=False)
        val_df.to_csv('yelp_reviews_val.csv', index=False)
        test_df.to_csv('yelp_reviews_test.csv', index=False)
        print("\nSplit datasets saved to CSV files.")

    return train_df, val_df, test_df

train_data = load_data("yelp_reviews_train.csv")
print(train_data)