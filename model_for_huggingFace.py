import re
from huggingface_hub import InferenceClient
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv
import os

load_dotenv()

graphdb_url = os.getenv("GRAPHDB_URL")
token_hf = os.getenv("TOKEN_HF")

sparql = SPARQLWrapper(graphdb_url)
client = InferenceClient(api_key=token_hf)

rdf_schema = """
Prefixes:
- kg: <http://www.semanticweb.org/KG#>
- xsd: <http://www.w3.org/2001/XMLSchema#>

Clases:
- kg:articulo
- kg:ley

Propiedades de Datos:
- kg:Num_Articulo_articulo (dominio: kg:articulo, rango: xsd:int)
- kg:Num_Ley_articulo (dominio: kg:articulo, rango: xsd:int)
- kg:Descripcion_articulo (dominio: kg:articulo, rango: xsd:string)
- kg:Num_Ley_ley (dominio: kg:ley, rango: xsd:int)
- kg:Descripcion_ley (dominio: kg:ley, rango: xsd:string)

Propiedades de Objeto:
- kg:fk_Num_ley (dominio: kg:articulo, rango: kg:ley)
"""

question = "Muestrame la descripcion de todas cada ley"

prompt = f"""
Eres un experto en SPARQL y RDF, y tu tarea es generar consultas SPARQL precisas.Tomando en cuenta el siguiente esquema RDF:

    {rdf_schema}

    Utiliza los siguientes prefijos en la consulta:

    PREFIX kg: <http://www.semanticweb.org/KG#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    Genera una consulta SPARQL correcta que responda a la siguiente pregunta:

    "{question}"

    La consulta debe utilizar las clases y propiedades de datos y objetos respetando mayusculas y minusculas definidas en el esquema RDF proporcionado.

    Proporciona únicamente la consulta SPARQL encerrada entre tres acentos invertidos así:

    \`\`\`sparql
    [Tu consulta SPARQL aquí]
    \`\`\`
    
Valida tu sparql generado con el esquema RDF y corrige si existen errores.
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
#print(f"Model Responce:\n{responce}")

cleaned_response = responce.replace('\\`', '`')

# Opcional: Imprimir la respuesta limpiada
#print("Respuesta después de limpiar los backticks:")
#print(cleaned_response)

pattern = r"```(?:sparql)?\n(.*?)\n```"
match = re.search(pattern, cleaned_response, re.DOTALL)

if match:
    sparql_query = match.group(1)
    print("\nConsulta SPARQL extraída:")
    print(sparql_query)
else:
    print("No se encontró una consulta SPARQL en la respuesta.")
    
    
sparql.setQuery(sparql_query)
sparql.setReturnFormat(JSON)

results = sparql.query().convert()

prompt = f"""
Eres un experto en procesamiento de datos y tu tarea es transformar resultados de consultas SPARQL en un formato JSON estructurado. Dada la siguiente respuesta de GraphDB:

{results}

Y considerando la consulta SPARQL utilizada:

{sparql_query}

Extrae **únicamente** los datos obtenidos y genera un JSON que contenga los valores de las variables retornadas por la consulta.

El JSON debe tener el siguiente formato:

[
  {{ "variable1": valor1, "variable2": valor2, ... }},
  {{ "variable1": valor3, "variable2": valor4, ... }},
  ...
]

No incluyas explicaciones ni comentarios; proporciona **únicamente** el JSON con los datos extraídos.
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
print("Model Responce: ",responce)