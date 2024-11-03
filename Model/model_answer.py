import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

#translator_en = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")
#translator_es = pipeline("translation", model="Helsinki-NLP/opus-mt-en-es")

def get_translation(model,text):
  translation = model(text)[0]['translation_text']
  return translation

device = (
    "cuda"
    if torch.cuda.is_available()
    else "rocm"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using {device} device")

tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-3B-Instruct')
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained("custom_q_and_a").to(device)

#print(model)

def ModeloResponse (question): 
    messages = [
        {"role": "user", "content": question},
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize = True,
        add_generation_prompt = True, # Must add for generation
        return_tensors = "pt",
    ).to("cuda")
    
    from transformers import TextStreamer
    text_streamer = TextStreamer(tokenizer, skip_prompt = True)
    response = model.generate(input_ids = inputs, streamer = text_streamer, max_new_tokens = 128,
                    use_cache = True, temperature = 1.5, min_p = 0.1)
    return response

answer=ModeloResponse("¿Qué delitos menciona el artículo 218 sobre el ejercicio ilegal de la medicina?")
print(answer)