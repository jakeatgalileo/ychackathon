from transformers import Trainer as HfTrainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_metric
from abc import ABC, abstractmethod

class Algorithm(ABC):
    @abstractmethod
    def train(self) -> dict:
        pass

class TextClassification(Algorithm):
    def __init__(self, train_dataset, valid_dataset, metric, target):
        self.train_dataset = train_dataset
        self.valid_dataset = valid_dataset
        self.metric = metric
        self.target = target
        self.model_name = "distilbert-base-uncased"
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=self.target)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def tokenize_function(self, examples):
        return self.tokenizer(examples["text"], padding="max_length", truncation=True)

    def train(self) -> dict:
        self.train_dataset = self.train_dataset.map(self.tokenize_function, batched=True)
        self.valid_dataset = self.valid_dataset.map(self.tokenize_function, batched=True)

        training_args = TrainingArguments(
            output_dir="./results",
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
        )

        trainer = HfTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.valid_dataset,
            compute_metrics=self.metric,
        )

        trainer.train()
        results = trainer.evaluate()
        return results

class AlgorithmFactory:
    @staticmethod
    def get_algorithm(task: str, train_dataset, valid_dataset, metric, target) -> Algorithm:
        if task == "text-classification":
            return TextClassification(train_dataset, valid_dataset, metric, target)
        else:
            raise ValueError(f"Unknown task: {task}")

class Trainer:
    def __init__(self, train_dataset, valid_dataset, task: str, metric, target):
        self.algorithm = AlgorithmFactory.get_algorithm(task, train_dataset, valid_dataset, metric, target)

    def train(self) -> dict:
        return self.algorithm.train()
