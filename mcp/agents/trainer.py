from datasets import load_dataset

import anthropic
import multiprocessing
import os


class Trainer:
    def __init__(self,
                 dataset_path: str,
                 task: str,
                 metric: str,
                 target: str,
                 num_clones: int):
        self.dataset_path = dataset_path
        self.task = task
        self.metric = metric
        self.target = target
        self.num_clones = num_clones
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        self.init_prompt = f"""
        You are a machine learning research agent operating in python. You have access to the following libraries: scikit-learn, numpy, transformers, datasets, pandas.
        Here are your task parameters:
          - Task: {self.task}
          - Metric: {self.metric}
          - Target: {self.target}
          - Dataset examples: {self.get_training_preview()}
          
        Please write a python training script that takes a csv dataset path as an argument and trains a machine 
        learning model to predict the target column {self.target} in those datasets.
        
        We will invoke your output with:
        `exec(your_verbatim_output, {{}}, {{"dataset_path": dataset_path}})`
        
        Save the model and results to the results/ directory.
        """

    def get_training_preview(self):
        # Load the dataset and extract examples
        assert os.path.exists(self.dataset_path), (f"Load dataset function checked '{self.dataset_path=}' "
                                                   f"but no such file exists.")
        dataset = load_dataset('csv', data_files=self.dataset_path)['train'][:2]
        stringified_train_previews = [str(row['text']) for row in dataset]
        return stringified_train_previews

    def generate_training_script(self):
        # Generate a training script using Anthropic sonnet 3.7
        prompt = self.init_prompt

        response = self.client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].text.strip()

    def run_training_script(self, script, retries=3):
        # Run the training script and handle errors
        for attempt in range(retries):
            try:
                exec(script, {}, {"dataset_path": self.dataset_path})
                return True
            except Exception as e:
                print(f"Error: {e}")
                script = self.generate_training_script_with_error(script, str(e))
        return False

    def generate_training_script_with_error(self, script, error):
        # Generate a new training script with the error context
        error_prompt = f"INSTRUCTIONS:\n{self.init_prompt}\n\nSCRIPT:\n{script}\n\nERROR: {error}\n\nPlease fix the error in the script. Return ONLY the script."
        response = self.client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": error_prompt}
            ]
        )
        return response.choices[0].text.strip()

    def train(self):
        # Spin off K processes and save trained models
        # Save trained models to a local model directory
        if not os.path.exists("models"):
            os.makedirs("models")

        processes = []
        for _ in range(self.num_clones):
            p = multiprocessing.Process(target=self.generate_and_run_script, args=())
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

    def generate_and_run_script(self):
        script = self.generate_training_script()
        self.run_training_script(script)


if __name__ == "__main__":
    trainer = Trainer("C:/Users/nickm/develop/mcp-yc25-hackathon/data/dataset.csv", "classification", "accuracy", "label", 5)
    trainer.train()
