from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer
import numpy as np

import evaluate

default_training_args = Seq2SeqTrainingArguments(
        output_dir="BART_v2",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=4,
        predict_with_generate=True
        )

class BingChillin:

    def __init__(self,checkpoint,dataset):

        self.checkpoint = checkpoint 

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
        self.data_collator = DataCollatorForSeq2Seq(tokenizer=self.tokenizer,
                                                    model=self.model)
        self.dataset = dataset
        
    def tokenize_dataset(self):
        
        def preprocess_function(examples):
            model_inputs = self.tokenizer(self.dataset['prompt'],
    
                                      max_length=1024, truncation=True)
            labels = self.tokenizer(text_target=self.dataset["summary"],
                                max_length=150, truncation=True)

            model_inputs["labels"] = labels["input_ids"]

            return model_inputs
        
        tokenized_dataset = self.dataset.map(preprocess_function, batched=True)
        
        self.tokenize_dataset = tokenized_dataset

    
    def train_summarizer(self,training_args=default_training_args):
        rouge = evaluate.load("rouge")

        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            decoded_preds = self.tokenizer.batch_decode(predictions,
                                                        skip_special_tokens=True)
            labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
            decoded_labels = self.tokenizer.batch_decode(labels, skip_special_tokens=True)

            result = rouge.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)

            prediction_lens = [np.count_nonzero(pred != self.tokenizer.pad_token_id) for pred in predictions]
            result["gen_len"] = np.mean(prediction_lens)

            return {k: round(v, 4) for k, v in result.items()}
        

        trainer = Seq2SeqTrainer(
        model=self.model,
        args=training_args,
        train_dataset=self.tokenized_dataset["train"],
        eval_dataset=self.tokenized_dataset["test"],
        tokenizer=self.tokenizer,
        data_collator=self.data_collator,
        compute_metrics=compute_metrics,
        )

        trainer.train()

        self.tuned_model = trainer.model


