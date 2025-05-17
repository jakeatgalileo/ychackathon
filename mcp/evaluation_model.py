import csv
import random
from collections import Counter

def evaluate_rows(filepath):
    """
    Processes a CSV file, generates random scores, and compares them to actual labels.
    
    Args:
        filepath (str): Path to the CSV file with review data
        
    Returns:
        dict: A dictionary containing:
            - 'predictions': List of random scores (0-4) for each row
            - 'actuals': List of actual labels from the CSV
            - 'stats': Dictionary with accuracy and distribution metrics
            - 'summary': Human and LLM-friendly text summary of results
    """
    random_scores = []
    actual_labels = []
    
    with open(filepath, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        # Skip header row
        headers = next(csv_reader)
        
        # Process each row
        for row in csv_reader:
            if len(row) > 0:
                # Generate random score (0-4)
                score = random.randint(0, 4)
                random_scores.append(score)
                
                # Extract actual label if available
                if len(row) > 0 and row[0].isdigit():
                    actual_labels.append(int(row[0]))
    
    # Calculate statistics
    stats = calculate_stats(random_scores, actual_labels)
    
    # Generate human/LLM readable summary
    summary = generate_summary(random_scores, actual_labels, stats)
    
    # Return comprehensive result
    result = {
        'predictions': random_scores,
        'actuals': actual_labels,
        'stats': stats,
        'summary': summary
    }
    
    return result

def calculate_stats(predictions, actuals):
    """Calculate accuracy and distribution statistics."""
    stats = {}
    
    if actuals:
        # Calculate accuracy
        correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
        stats['accuracy'] = round(correct / len(actuals) * 100, 2)
        
        # Calculate prediction distribution
        stats['prediction_distribution'] = dict(Counter(predictions))
        
        # Calculate actual distribution
        stats['actual_distribution'] = dict(Counter(actuals))
        
        # Calculate distribution of differences
        diffs = [abs(p - a) for p, a in zip(predictions, actuals)]
        stats['avg_error'] = round(sum(diffs) / len(diffs), 2)
        stats['error_distribution'] = dict(Counter(diffs))
    else:
        stats['note'] = "No actual labels found for comparison"
    
    return stats

def generate_summary(predictions, actuals, stats):
    """Generate a human and LLM-friendly summary of the evaluation results."""
    summary = f"Evaluation Summary\n{'='*20}\n"
    
    # Basic counts
    summary += f"Total reviews processed: {len(predictions)}\n"
    
    if actuals:
        # Accuracy metrics
        summary += f"Model accuracy: {stats['accuracy']}%\n"
        summary += f"Average error: {stats['avg_error']} stars\n\n"
        
        # Distribution information
        summary += "Distribution of predicted ratings:\n"
        for rating in range(5):
            count = stats['prediction_distribution'].get(rating, 0)
            pct = round(count / len(predictions) * 100, 1)
            summary += f"  {rating} stars: {count} reviews ({pct}%)\n"
        
        summary += "\nDistribution of actual ratings:\n"
        for rating in range(5):
            count = stats['actual_distribution'].get(rating, 0)
            pct = round(count / len(actuals) * 100, 1) if len(actuals) > 0 else 0
            summary += f"  {rating} stars: {count} reviews ({pct}%)\n"
        
        summary += "\nError distribution:\n"
        for diff in sorted(stats['error_distribution'].keys()):
            count = stats['error_distribution'][diff]
            pct = round(count / len(predictions) * 100, 1)
            summary += f"  Off by {diff} stars: {count} reviews ({pct}%)\n"
    else:
        summary += "No actual labels found for comparison.\n"
        summary += "Generated random predictions only.\n\n"
        
        summary += "Distribution of predicted ratings:\n"
        for rating in range(5):
            count = stats['prediction_distribution'].get(rating, 0)
            pct = round(count / len(predictions) * 100, 1)
            summary += f"  {rating} stars: {count} reviews ({pct}%)\n"
    
    return summary

print(evaluate_rows("/Users/cjache/repos/ychackathon/mcp/datasets/yelp_reviews_test.csv"))