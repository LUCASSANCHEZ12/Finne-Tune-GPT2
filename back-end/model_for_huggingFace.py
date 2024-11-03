import re
from huggingface_hub import InferenceClient
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

def consult_knowledge_graph(question):
    # Retrieve environment variables
    graphdb_url = os.getenv("GRAPHDB_URL")
    token_hf = os.getenv("TOKEN_HF")

    # Initialize SPARQLWrapper with the GraphDB URL
    sparql = SPARQLWrapper(graphdb_url)
    # Initialize HuggingFace InferenceClient with the API token
    client = InferenceClient(api_key=token_hf)

    # RDF schema definition
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

    # Example SPARQL queries
    example_pregunta_ley = """
    PREFIX kg: <http://www.semanticweb.org/KG#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?Descripcion_ley
    WHERE {
        ?ley kg:Num_Ley_ley 26 .
        ?ley kg:Descripcion_ley ?Descripcion_ley .
    }
    """

    example_pregunta_articulo = """
    PREFIX kg: <http://www.semanticweb.org/KG#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?Descripcion_articulo ?num_ley
    WHERE {
        ?articulo a kg:articulo ;
            kg:Num_Articulo_articulo 5135 ;
            kg:Descripcion_articulo ?Descripcion_articulo ;
            kg:fk_Num_ley ?ley .
        ?ley kg:Num_Ley_ley ?num_ley .
        FILTER(?num_ley = 26)
    }
    """

    example_pregunta_ley_2= """
    PREFIX kg: <http://www.semanticweb.org/KG#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?num_ley ?Descripcion_ley ?Descripcion_articulo ?num_articulo
    WHERE {
        ?articulo a kg:articulo ;
            kg:Num_Articulo_articulo ?num_articulo ;
            kg:Descripcion_articulo ?Descripcion_articulo ;
            kg:fk_Num_ley ?ley .
        ?ley kg:Num_Ley_ley ?num_ley ;
                kg:Descripcion_ley ?Descripcion_ley .
        FILTER(?num_ley = 26)
    }
    """
    
    # Prompt for generating SPARQL query based on user question
    prompt = f"""
    Eres un experto en SPARQL y RDF. Tu tarea es generar consultas SPARQL correctas basadas en el esquema RDF proporcionado, siguiendo cuidadosamente el formato y las instrucciones.

    **Esquema RDF**:

    {rdf_schema}

    Usa los prefijos:
    PREFIX kg: <http://www.semanticweb.org/KG#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    ### Ejemplos de Preguntas y Consultas SPARQL

    - **Pregunta**: "¿Qué establece la ley número 26?" o "Explica la ley 26."
    \`\`\`sparql
    {example_pregunta_ley}
    \`\`\`

    - **Pregunta**: "¿Qué dice el artículo número 5135 de la ley 26?" o "Explica el artículo 5135 de la ley 26."
    \`\`\`sparql
    {example_pregunta_articulo}
    \`\`\`

    - **Pregunta**: "Explica la ley 26 con todos sus artículos."
    \`\`\`sparql
    {example_pregunta_ley_2}
    \`\`\`

    **Instrucciones importantes**:

    1. **Formato de SELECT y Variables**:
    - Coloca un espacio después de `SELECT` y antes de las variables, así: `SELECT ?num_ley ?Descripcion_ley`.
    - Usa un espacio entre cada propiedad y su variable, así: `kg:Num_Articulo_articulo ?num_articulo`.

    2. **Relación entre `articulo` y `ley`**:
    - Usa `kg:fk_Num_ley` **solo en una dirección**: desde `articulo` hacia `ley`.

    3. **Estructura de las Tripletas**:
    - Para múltiples propiedades de una misma entidad, usa `;` al final de cada línea.
    - Termina cada bloque de tripletas con un punto (`.`).

    4. **Definición de Entidades**:
    - Define cada entidad usando `a kg:articulo` para un artículo y `a kg:ley` para una ley.

    Pregunta del usuario: "{question}"

    **Formato de Entrega**:

    Proporciona solo la consulta en este formato, sin comentarios adicionales:

    \`\`\`sparql
    [TU CONSULTA SPARQL]
    \`\`\`
    """

    # Prepare the message for the HuggingFace model
    messages = [
        { "role": "user", "content": prompt }
    ]

    # Generate the SPARQL query using the HuggingFace model
    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct", 
        messages=messages, 
        max_tokens=500,
        stream=False
    )

    # Extract the SPARQL query from the model's response
    responce = stream.choices[0].message.content
    cleaned_response = responce.replace('\\`', '`')
    pattern = r"```(?:sparql)?\n(.*?)\n```"
    match = re.search(pattern, cleaned_response, re.DOTALL)

    if match:
        sparql_query = match.group(1)
    else:
        raise Exception("No se encontró una consulta SPARQL en la respuesta.")
    
    print(sparql_query)
        
    try:    
        sparql.setQuery(sparql_query)
        sparql.setReturnFormat(JSON)
        
        # Execute the SPARQL query and get the results
        results = sparql.query().convert()
        print(results)
    except Exception as e:
        raise Exception("Error con el sparql.")

    # Prompt for generating a natural language response based on the SPARQL results
    prompt = f"""
    Eres un experto en lenguaje natural. Transforma la siguiente respuesta de GraphDB en JSON:

    {results}

    Pregunta del usuario: "{question}"

    **Objetivo**:
    Genera una respuesta en español que sea clara y responda directamente a la pregunta.

    **Requisitos**:
    - Usa lenguaje natural sin detalles técnicos.
    - No menciones que la información proviene de una base de datos.

    Ejemplos:
    - Para una descripción de ley: "La ley número 26 establece que...".
    - Para varios artículos: "El artículo <número> de la ley <número> establece que...".
    - Si no hay resultados, indica que no se encontraron respuestas.

    Entrega solo la respuesta en español.
    """

    # Prepare the message for the HuggingFace model
    messages = [
        { "role": "user", "content": prompt }
    ]

    try:
        # Generate the natural language response using the HuggingFace model
        stream = client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct", 
            messages=messages, 
            max_tokens=500,
            stream=False
        )
    except Exception as e:
        raise Exception("Consulta demasiado larga.")

    # Extract the natural language response from the model's response
    response = stream.choices[0].message.content
    print(f"\n\n-----------------------------------Model Response-----------------------------------\n\n{response}\n\n------------------------------------------------------------------------------------\n\n")

    return response

# Unit Test
question = "Explica la ley 26 con todos sus artículos."
#consult_knowledge_graph(question)