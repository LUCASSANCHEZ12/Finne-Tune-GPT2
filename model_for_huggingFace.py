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
  
  Propiedades de objeto:
  
    <owl:ObjectProperty rdf:about="http://www.semanticweb.org/KG#fk_Num_ley">
        <rdfs:domain rdf:resource="http://www.semanticweb.org/KG#articulo"/>
        <rdfs:range rdf:resource="http://www.semanticweb.org/KG#ley"/>
    </owl:ObjectProperty>
  
  Propiedades de datos:
  
    <owl:DatatypeProperty rdf:about="http://www.semanticweb.org/KG#Num_Ley_ley">
        <rdfs:domain rdf:resource="http://www.semanticweb.org/KG#ley"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#int"/>
    </owl:DatatypeProperty>
    
    <owl:DatatypeProperty rdf:about="http://www.semanticweb.org/KG#Num_Articulo_articulo">
        <rdfs:domain rdf:resource="http://www.semanticweb.org/KG#articulo"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#int"/>
    </owl:DatatypeProperty>
  
    <owl:DatatypeProperty rdf:about="http://www.semanticweb.org/KG#Descripcion_ley">
        <rdfs:domain rdf:resource="http://www.semanticweb.org/KG#ley"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
    </owl:DatatypeProperty>
  
    <owl:DatatypeProperty rdf:about="http://www.semanticweb.org/KG#Num_ley_articulo">
        <rdfs:domain rdf:resource="http://www.semanticweb.org/KG#articulo"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#int"/>
    </owl:DatatypeProperty>
    
    <owl:DatatypeProperty rdf:about="http://www.semanticweb.org/KG#Descripcion_articulo">
        <rdfs:domain rdf:resource="http://www.semanticweb.org/KG#articulo"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
    </owl:DatatypeProperty>
  
  Clases:
  
  <owl:Class rdf:about="http://www.semanticweb.org/KG#ley"/>
  
  <owl:Class rdf:about="http://www.semanticweb.org/KG#articulo"/>
"""

example = """
PREFIX kg: <http://www.semanticweb.org/KG#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?Descripcion_ley
WHERE {
    ?ley kg:Num_Ley_ley 26 .
    ?ley kg:Descripcion_ley ?Descripcion_ley .
}
"""

question = "Describe la ley 26 con todos sus articulos"

prompt = f"""
Eres un experto en SPARQL y RDF. Tu tarea es generar consultas SPARQL precisas y correctas basadas en el esquema RDF proporcionado. A continuación se muestra el esquema RDF:

{rdf_schema}

Utiliza los siguientes prefijos en la consulta:

PREFIX kg: <http://www.semanticweb.org/KG#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

Es **crucial** que utilices las clases y propiedades **exactamente** como aparecen en el esquema RDF, respetando mayúsculas y minúsculas.

Genera **únicamente** la consulta SPARQL correcta que responda a la siguiente pregunta, sin añadir explicaciones ni comentarios adicionales:

"{question}"

La consulta debe:

- Ser lo mas simple posible sin funciones innecesarias y parametros que no se usan.
- Utilizar las clases y propiedades de datos y objetos tal como están definidas en el esquema RDF.
- Respetar mayúsculas y minúsculas.
- Ser sintácticamente correcta y válida según el esquema RDF proporcionado.

Proporciona únicamente la consulta SPARQL encerrada entre tres acentos invertidos así:

\`\`\`sparql
[Tu consulta SPARQL aquí]
\`\`\`

Antes de proporcionar la consulta final, verifica que la misma es correcta y cumple con todos los requisitos.

**Ejemplo de una consulta SPARQL válida:**

Si la pregunta fuera "¿Cuál es la descripción de la ley con número 26?", la consulta SPARQL sería:

\`\`\`sparql
{example}
\`\`\`

Ahora, genera la consulta SPARQL que responde a la pregunta proporcionada.
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
Eres un experto en lenguaje natural y tu tarea es interpretar los resultados de consultas SPARQL y proporcionar respuestas verbalizadas en español.

Dada la siguiente respuesta de GraphDB:

{results}

Y considerando la consulta SPARQL utilizada:

{sparql_query}

Genera una respuesta en lenguaje natural que comunique claramente la información obtenida, respondiendo a la pregunta original:

"{question}"

La respuesta debe:

- Ser clara y concisa.
- Incluir los datos relevantes obtenidos de la consulta.
- Estar redactada en español correcto.
- No incluir información técnica ni detalles de la consulta.

No incluyas explicaciones adicionales ni comentarios técnicos; proporciona **únicamente** la respuesta verbalizada al usuario.
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