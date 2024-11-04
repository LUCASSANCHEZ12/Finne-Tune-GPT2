import re
import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def make_decision(user_prompt):
    # Retrieve the Hugging Face API token from environment variables
    token_hf = os.getenv("TOKEN_HF")

    # Initialize the InferenceClient with the API token
    client = InferenceClient(api_key=token_hf)

    # Construct the prompt for the model
    prompt = f"""
    Eres un asistente que clasifica preguntas legales como **"Específica"** o **"Inferencial"**.

    **Definiciones**:

    - **Pregunta Específica**: Pregunta directamente sobre una ley o artículo en particular y sin preguntas simples y sencillas. Hace referencia explícita a documentos legales o artículos específicos.

    **Ejemplos de Preguntas Específicas**:
    - "¿Qué establece la ley número 26?"
    - "Explica la ley 26"
    - "¿Qué dice el artículo número 5135 de la ley 26?"
    - "Explica el artículo 5135 de la ley 26"
    - "Explica la ley 26 con todos sus artículos"

    - **Pregunta Inferencial**: Pregunta sobre un tema, escenario legal y son preguntas mas complejas. Requiere inferir qué leyes,articulos o derechos aplican.

    **Ejemplos de Preguntas Inferenciales**:
    - "¿Que ley me sanciona en caso de asesinato?"
    - "¿Qué ley me protege en caso de asesinato?"
    - "¿Qué penalización sufro en caso de asesinato?"
    - "¿Qué derechos se garantizan en el artículo 23 sobre la libertad y seguridad personal?"
    - "¿Qué establece el artículo 33 sobre el derecho al medio ambiente?"
    - "¿Qué artículo agrava las penas si se cometen actos con circunstancias como alevosía o ensañamiento?"
    - "¿Qué artículo establece una mayor sanción si la víctima de homicidio es un niño, niña o adolescente?"
    - "¿Qué tipo de acciones nacen de la comisión de un delito según el artículo 14?"

    **Instrucciones**:

    - Dada la siguiente pregunta, determina si es una **"Específica"** o **"Inferencial"**.
    - **Responde únicamente** con la palabra **"Específica"** o **"Inferencial"**, sin añadir ningún otro texto.
    - No añadas explicaciones, saludos, despedidas ni información adicional.

    **Pregunta**:

    "{user_prompt}"
    """
    
    # Create the message payload for the model
    messages = [
        { "role": "user", "content": prompt }
    ]

    # Send the prompt to the model and get the response
    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct", 
        messages=messages, 
        max_tokens=500,
        stream=False
    )
    
    # Extract the response content
    response = stream.choices[0].message.content
    return response

# Unit Test
#make_decision("¿Cuál es la responsabilidad del Estado respecto a la educación según el artículo 77?")