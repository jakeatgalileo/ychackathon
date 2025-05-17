from typing import Dict, List, Any, Optional

class DatasetTools:
    """Tools for analyzing and processing datasets."""
    
    @staticmethod
    def analyze_data_types(columns: List[str], sample_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Determine the likely data types for each column in the dataset.
        
        Args:
            columns: List of column names
            sample_data: Sample rows of data
            
        Returns:
            Dictionary mapping column names to inferred data types
        """
        if not sample_data:
            return {col: "unknown" for col in columns}
        
        data_types = {}
        
        for col in columns:
            # Get non-empty values
            values = [row.get(col) for row in sample_data if row.get(col)]
            
            if not values:
                data_types[col] = "unknown"
                continue
                
            # Check if all values could be numeric
            try:
                all_float = all(float(val) for val in values)
                if all_float:
                    # Check if all are integers
                    if all(float(val) == int(float(val)) for val in values):
                        data_types[col] = "integer"
                    else:
                        data_types[col] = "float"
                    continue
            except ValueError:
                pass
                
            # Check if values look like dates
            date_indicators = ["-", "/", ":", "T", "Z"]
            if any(any(ind in str(val) for ind in date_indicators) for val in values):
                data_types[col] = "datetime"
                continue
                
            # Default to string
            data_types[col] = "string"
            
        return data_types
    
    @staticmethod
    def identify_target_column(columns: List[str]) -> Optional[str]:
        """
        Try to identify which column is likely the target variable.
        
        Args:
            columns: List of column names
            
        Returns:
            Name of the likely target column, or None if uncertain
        """
        target_indicators = ["target", "label", "class", "outcome", "result", "prediction", "y"]
        
        for indicator in target_indicators:
            # Exact match
            if indicator in columns:
                return indicator
                
            # Look for columns containing the indicator
            for col in columns:
                if indicator in col.lower():
                    return col
                    
        return None
    
    @staticmethod
    def suggest_ml_tasks(columns: List[str], data_types: Dict[str, str]) -> List[str]:
        """
        Suggest possible machine learning tasks based on the dataset structure.
        
        Args:
            columns: List of column names
            data_types: Dictionary mapping column names to data types
            
        Returns:
            List of suggested ML tasks
        """
        tasks = []
        
        # Check for classification indicators
        classification_indicators = ["class", "category", "label", "type", "group"]
        has_classification = any(ind in col.lower() for ind in classification_indicators for col in columns)
        
        if has_classification:
            tasks.append("classification")
            
        # Check for regression indicators
        regression_indicators = ["value", "price", "amount", "score", "rating"]
        has_regression = any(ind in col.lower() for ind in regression_indicators for col in columns)
        
        if has_regression:
            tasks.append("regression")
            
        # Check for time series indicators
        time_indicators = ["date", "time", "day", "month", "year", "timestamp"]
        has_time = any(ind in col.lower() for ind in time_indicators for col in columns)
        
        if has_time:
            tasks.append("time series analysis")
            
        # Check for clustering potential (when no clear target)
        if not has_classification and not has_regression:
            tasks.append("clustering")
            
        # When we have text fields, suggest NLP
        text_indicators = ["text", "description", "comment", "review", "message"]
        has_text = any(ind in col.lower() for ind in text_indicators for col in columns) or \
                  any(dt == "string" for dt in data_types.values())
        
        if has_text:
            tasks.append("natural language processing")
            
        # Default if nothing detected
        if not tasks:
            tasks.append("exploratory data analysis")
            
        return tasks 