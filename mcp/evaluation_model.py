import csv
import random

def evaluate_rows(filepath):
    random_scores = []
    
    with open(filepath, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        # Skip header row if it exists
        next(csv_reader, None)
        
        for row in csv_reader:
            score = random.randint(0, 4)
            random_scores.append(score)
    
    return random_scores