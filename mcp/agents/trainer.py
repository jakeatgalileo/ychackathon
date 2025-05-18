from datasets import load_dataset
from datetime import datetime
from dotenv import load_dotenv

import anthropic
import multiprocessing
import os
import pandas as pd
import shutil
import traceback

load_dotenv("../../.env")


def generate(dataset_path, task, metric, target):
    trainer = Trainer(dataset_path=dataset_path,
                      task=task,
                      metric=metric,
                      target=target)
    trainer.run()


def generate_and_run_script(dataset_path: str,
                            task: str,
                            metric: str,
                            target: str,
                            num_clones: int = 1,
                            output_dir: str = "results"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processes = []
    for _ in range(num_clones):
        p = multiprocessing.Process(
            target=generate,
            args=(dataset_path, task, metric, target)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


class Trainer:
    def __init__(self,
                 dataset_path: str,
                 task: str,
                 metric: str,
                 target: str,
                 be_fast: bool = True):
        self.dataset_path = dataset_path
        self.task = task
        self.metric = metric
        self.target = target
        self.expected_output_directory_template = "((expected_output_directory))"
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        self.init_prompt = f"""
        You are a machine learning research agent operating in python. You have access to the following libraries: scikit-learn, numpy, transformers, datasets, pandas, and torch.
        Here are your task parameters:
          - Task: {self.task}
          - Metric: {self.metric}
          - Target: {self.target}
          - Dataset examples: {self.get_training_preview()}
          
        Please write a python training script as a string that takes a csv dataset path as an argument and trains a machine 
        learning model to predict the target column {self.target} in those datasets. Only output the code and no other exposition OR markdown code fences.
        
        We will invoke your output with:
        `exec(your_verbatim_output, {{}}, {{"dataset_path": dataset_path}})`
        
        Save the model and results to a subfolder in the results/ directory named '{self.expected_output_directory_template}'.
        {"You only have 10 minutes to train, so set your hyperparameters to be as fast as possible, e.g. 1 epoch, etc." if be_fast else ""}
        """

    def get_training_preview(self):
        # Load the dataset and extract examples
        assert os.path.exists(self.dataset_path), (f"Load dataset function checked '{self.dataset_path=}' "
                                                   f"but no such file exists.")
        stringified_dataset_preview = pd.DataFrame(
            load_dataset('csv', data_files=self.dataset_path)['train'][:2]
        ).to_string(index=False, max_colwidth=100)
        return stringified_dataset_preview

    def output_directory(self):
        now = datetime.now()
        # Format it as YYYY-MM-DD-HH-MM
        return f"{self.task}-{now.strftime('%Y-%m-%d-%H-%M')}"

    def generate_training_script(self):
        # Generate a training script using Anthropic sonnet 3.7
        expected_output = self.output_directory()
        prompt = self.init_prompt.replace(self.expected_output_directory_template, expected_output)

        response = self.client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ],
            thinking={
                "type": "enabled",
                "budget_tokens": 1024
            }
        )
        script = response.content[-1].text.strip()
        print(f"Generated script:\n\n{script}")
        return script, expected_output

    def run_training_script(self, script, expected_output, retries=5):
        # Run the training script and handle errors
        current_dir = os.path.dirname(os.path.realpath(__file__))
        full_expected_output = os.path.join(current_dir, "results", expected_output)

        for attempt in range(retries):
            try:
                exec(script, {"dataset_path": self.dataset_path})
                assert (os.path.exists(full_expected_output)
                        and os.path.isdir(full_expected_output)
                        and len(os.listdir(full_expected_output)) > 0), \
                    f"Expected {expected_output} is either empty, not a directory, or does not exist."
                return True
            except Exception as e:
                tb_str = traceback.format_exc()
                err_string = f"Error for last attempt ({attempt + 1}/{retries}): {e}\n\n{tb_str}"
                print(err_string)
                # Clean up directory, in case it has anything from last run.
                if os.path.exists(full_expected_output):
                    shutil.rmtree(full_expected_output)
                script = self.generate_training_script_with_error(script, expected_output, err_string)
        return False

    def generate_training_script_with_error(self, script, expected_output, error):
        # Generate a new training script with the error context
        instructions = self.init_prompt.replace(self.expected_output_directory_template, expected_output)
        error_prompt = f"INSTRUCTIONS:\n{instructions}\n\nSCRIPT:\n{script}\n\nERROR: {error}\n\nPlease fix the error in the script. Return ONLY the script."
        response = self.client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=5120,
            messages=[
                {"role": "user", "content": error_prompt}
            ],
            thinking={
                "type": "enabled",
                "budget_tokens": 1024
            }
        )
        script = response.content[-1].text.strip()
        print(f"Generated revised script:\n\n{script}")
        return script

    def run(self):
        script, expected_output = self.generate_training_script()
        self.run_training_script(script, expected_output)


if __name__ == "__main__":
    # generate_and_run_script("C:/Users/nickm/develop/mcp-yc25-hackathon/data/dataset.csv",
    #                         "classification",
    #                         "accuracy",
    #                         "label",
    #                         1)
    generate_and_run_script("C:/Users/nickm/develop/mcp-yc25-hackathon/data/logistic_regression_dataset.csv",
                            "classification",
                            "accuracy",
                            "target",
                            1)
