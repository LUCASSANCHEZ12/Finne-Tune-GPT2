import re
import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
def make_decision(user_prompt):
    token_hf = os.getenv("TOKEN_HF")

    client = InferenceClient(api_key=token_hf)

    prompt = f"""
    Eres un asistente que clasifica preguntas legales como **"Específica"** o **"Inferencial"**.

    **Definiciones**:

    - **Pregunta Específica**: Pregunta directamente sobre una ley o artículo en particular por número sin mencionar sobre que area. Hace referencia explícita a documentos legales o artículos específicos.

    **Ejemplos de Preguntas Específicas**:
    - "¿Qué establece la ley número 26?"
    - "Explica la ley 26."
    - "¿Qué dice el artículo número 5135 de la ley 26?"
    - "Explica el artículo 5135 de la ley 26."
    - "Explica la ley 26 con todos sus artículos."

    - **Pregunta Inferencial**: Pregunta sobre un tema, escenario legal o articulo en cierta area. Requiere inferir qué leyes,articulos o derechos aplican.

    **Ejemplos de Preguntas Inferenciales**:
    - "¿Qué ley me protege en caso de asesinato?"
    - "¿Qué penalización sufro en caso de asesinato?"
    - ¿Qué derechos se garantizan en el artículo 23 sobre la libertad y seguridad personal?
    - ¿Qué establece el artículo 33 sobre el derecho al medio ambiente?

    **Instrucciones**:

    - Dada la siguiente pregunta, determina si es una **"Específica"** o **"Inferencial"**.
    - **Responde únicamente** con la palabra **"Específica"** o **"Inferencial"**, sin añadir ningún otro texto.
    - No añadas explicaciones, saludos, despedidas ni información adicional.

    **Pregunta**:

    "{user_prompt}"
    """
    
    messages = [
        { "role": "user", "content": prompt }
    ]

    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct", 
        messages=messages, 
        max_tokens=500,
        stream=False
    )
    
    responce = stream.choices[0].message.content
    return responce

make_decision("¿Cuál es la responsabilidad del Estado respecto a la educación según el artículo 77?")