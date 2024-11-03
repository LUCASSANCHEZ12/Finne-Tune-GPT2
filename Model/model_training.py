import torch
import math
import pandas as pd
import transformers
import torch.nn as nn
import evaluate
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from transformers import TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training


# Set logging level to suppress unnecessary output
transformers.logging.set_verbosity_error()

# Select device (GPU, ROCm, or CPU) for model training
device = (
    "cuda"
    if torch.cuda.is_available()
    else "rocm"
    if torch.backends.mps.is_available()
    else "cpu"
)

# Load the tokenizer and set pad token
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-3B-Instruct')
tokenizer.pad_token = tokenizer.eos_token

# Function to load and tokenize datasets from file path
def load_datasets(file_path, tokenizer, block_size=64):
    datasets = load_dataset('text', data_files={'train': file_path})
    tokenized_datasets = datasets.map(
        lambda examples: tokenizer(examples['text'], truncation=True, padding='max_length', max_length=block_size),
        batched=True
    )
    return tokenized_datasets['train']

# Function to prepare data collator for language modeling
def load_data_collator(tokenizer, mlm = False):
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=mlm,
    )
    return data_collator

# Load accuracy metric for evaluation
accuracy_metric = evaluate.load("accuracy")

# Function to compute metrics (accuracy and perplexity)
def compute_metrics(eval_pred):
    logits, labels = eval_pred

    # Convert logits to PyTorch tensor if it is a numpy array
    if isinstance(logits, np.ndarray):
        logits = torch.tensor(logits)

    # Shift logits and labels
    shift_logits = logits[..., :-1, :].contiguous()  # Ensure that logits are a tensor to apply contiguous
    shift_labels = torch.tensor(labels[..., 1:])     # Ensure that labels are also tensioners

    # CrossEntropy loss for calculating perplexity
    loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
    loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

    # Calculate perplexity
    perplexity = math.exp(loss)

    # Calculate accuracy using accuracy metric
    predictions = torch.argmax(shift_logits, dim=-1).detach().cpu().numpy()
    labels = shift_labels.detach().cpu().numpy()
    accuracy = accuracy_metric.compute(predictions=predictions.flatten(), references=labels.flatten())
    print(f"Accuracy: {accuracy['accuracy']}")

    return {
        "perplexity": perplexity
    }

# Main function to load data, configure model, and initiate training
def train(train_file_path,
          validation_file_path,
          model_name,
          output_dir,
          overwrite_output_dir,
          per_device_train_batch_size,
          num_train_epochs,
          lr):
    
    # Load and tokenize train and validation datasets
    train_dataset = load_datasets(train_file_path, tokenizer)
    eval_dataset = load_datasets(validation_file_path, tokenizer)
    data_collator = load_data_collator(tokenizer)
    
    # Save tokenizer to output directory
    tokenizer.save_pretrained(output_dir)
    
    # Configure LoRA for parameter-efficient fine-tuning
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj" ,"v_proj", "o_proj" , "gate_proj" , "up_proj" , "down_proj"], # Target query and value projection layers
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Load pretrained model and apply LoRA configuration
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_8bit=True,
        device_map="auto"
    )
    model = prepare_model_for_kbit_training(model) # Prepare model for training with k-bit precision
    model = get_peft_model(model, lora_config) # Apply LoRA configuration to the model
    
    # Resize token embeddings to fit tokenizer's vocab size
    model.resize_token_embeddings(len(tokenizer))
    model.print_trainable_parameters() # Print the parameters that will be trained
    
    # Set training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=overwrite_output_dir,
        per_device_train_batch_size=per_device_train_batch_size,
        per_device_eval_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=4, # Accumulate gradients over 4 steps
        num_train_epochs=num_train_epochs,
        evaluation_strategy="epoch", # Evaluate at the end of each epoch
        save_strategy="epoch",
        learning_rate=lr,
        weight_decay=0.01, # Regularization parameter
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False, # Lower eval_loss is better
        fp16=True, # Mixed precision training for efficiency
        save_total_limit=2, # Limit number of saved models
    )
    
    # Initialize trainer with model, data, and training configurations
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset
    )
    
    # Start training and save model
    trainer.train()
    trainer.save_model()

# Define parameters and file paths for training
model_name = "meta-llama/Llama-3.2-3B-Instruct"
train_file_path = "question_answers_train1.txt"
validation_file_path = "question_answers_validation1.txt"
output_dir = 'custom_q_and_a_2/'
overwrite_output_dir = True
# Hyperparameters for training
per_device_train_batch_size = 5
num_train_epochs = 50
lr = 5e-5

# Begin training process
train(
    train_file_path=train_file_path,
    validation_file_path=validation_file_path,
    model_name=model_name,
    output_dir=output_dir,
    overwrite_output_dir=overwrite_output_dir,
    per_device_train_batch_size=per_device_train_batch_size,
    num_train_epochs=num_train_epochs,
    lr=lr
)