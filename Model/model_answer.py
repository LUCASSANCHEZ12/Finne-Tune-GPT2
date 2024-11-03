import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Determine the device to use: GPU (CUDA) if available, else CPU
device = (
    "cuda"  # Use CUDA GPU if available
    if torch.cuda.is_available()
    else "rocm"  # Use ROCm if available
    if torch.backends.mps.is_available()
    else "cpu"  # Default to CPU
)
print(f"Using {device} device")

# Load the tokenizer for the specified pre-trained model
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-3B-Instruct')
tokenizer.pad_token = tokenizer.eos_token  # Set the padding token to the end-of-sequence token

# Load the pre-trained language model and move it to the selected device
model = AutoModelForCausalLM.from_pretrained("custom_q_and_a").to(device)

def ModelResponse(question):
    # Prepare the conversation with the user's question
    messages = [
        {"role": "user", "content": question},
    ]
    # Apply a chat template to format the input for the model
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,  # Must be added for text generation
        return_tensors="pt",
    ).to(device)
    # Generate the model's response
    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=128,  # Maximum number of tokens to generate
        use_cache=True,
        temperature=1.5,  # Sampling temperature for randomness
        min_p=0.1  # Minimum cumulative probability for nucleus sampling
    )
    # Extract the generated tokens excluding the input prompt
    generated_tokens = outputs[0][inputs.shape[-1]:]
    # Decode the tokens to obtain the generated text
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return generated_text

# Get the model's response to a specific question
answer = ModelResponse("¿Qué establece el artículo 168 sobre la autocalumnia?")
print(answer)  # Print the response