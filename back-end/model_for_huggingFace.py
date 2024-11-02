import re
from huggingface_hub import InferenceClient
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv
import os

load_dotenv()
def consult_knowledge_graph(question):
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

    SELECT ?Descripcion_articulo
    WHERE {
        ?articulo a kg:articulo ;
            kg:Num_Articulo_articulo 5135 ;
            kg:Descripcion_articulo ?Descripcion_articulo ;
            kg:fk_Num_ley ?ley .
        ?ley kg:Num_Ley_ley 26 .
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
    
    prompt = f"""
    Eres un experto en SPARQL y RDF. Tu tarea es generar consultas SPARQL precisas y correctas basadas en el esquema RDF proporcionado. 

    A continuación tienes el esquema RDF que define los elementos `Ley` y `Artículo`, y sus propiedades y relaciones, con el único vínculo a través de la propiedad `fk_Num_ley`.

    **Esquema RDF**:

    {rdf_schema}

    **Consulta SPARQL válida para preguntas sobre leyes o artículos**:

    Usa estos prefijos en cada consulta:
    PREFIX kg: <http://www.semanticweb.org/KG#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    ### Ejemplos de Preguntas y Respuestas SPARQL

    - **Pregunta**: "¿Qué establece la ley número 26?" o "Explica la ley 26."
    **Consulta SPARQL**:
    \`\`\`sparql
    {example_pregunta_ley}
    \`\`\`

    - **Pregunta**: "¿Qué dice el artículo número 5135 de la ley 26?" o "Explica el artículo 5135 de la ley 26." o "¿Que establece el articulo numero 5135 de la ley 26?
    **Consulta SPARQL**:
    \`\`\`sparql
    {example_pregunta_articulo}
    \`\`\`

    - **Pregunta**: "Explica la ley 26 con todos sus artículos" o "¿Qué contiene la ley 26?" o "Explica detalladamente la ley 26 con todos sus artículos."
    **Consulta SPARQL**:
    \`\`\`sparql
    {example_pregunta_ley_2}
    \`\`\`

    **Instrucciones para la consulta**:

    Genera solo la consulta SPARQL correcta en respuesta a la pregunta del usuario usando las clases y propiedades **exactamente** como en el esquema RDF, con mayúsculas y minúsculas correspondientes.

    **Antes de enviar la consulta, asegúrate de que sea válida y devuelva los resultados esperados. Valida y comprueba, si la consulta es incorrecta, genera una nueva consulta que sea correcta.**

    Pregunta del usuario: "{question}"

    Entrega la consulta en el formato:

    \`\`\`sparql
    [TU CONSULTA SPARQL]
    \`\`\`

    **No utilices caracteres especiales innecesarios en la consulta como: >, < Al inicio de cada linea**
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
        return
        
        
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    prompt = f"""
    Eres un experto en lenguaje natural y tu tarea es interpretar los resultados de consultas SPARQL y proporcionar respuestas en español que sean claras, concisas y de fácil comprensión para el usuario.

    Dada la siguiente respuesta obtenida de GraphDB en formato JSON:

    {results}

    La pregunta original del usuario es la siguiente:

    "{question}"

    **Objetivo**:
    Transforma la información obtenida en una respuesta en lenguaje natural, redactada de manera que responda específicamente a la pregunta del usuario y que sea comprensible para cualquier persona sin conocimientos técnicos.

    **Requisitos para la respuesta**:
    - La respuesta debe ser clara, directa y contener únicamente la información relevante a la pregunta.
    - La redacción debe ser en español correcto, sin incluir detalles técnicos ni términos específicos de RDF o SPARQL.
    - Evita mencionar que la información proviene de una base de datos; simplemente responde a la pregunta como si estuvieras explicando verbalmente.

    Ejemplo de transformación de respuesta:
    - Si la pregunta del usuario era sobre la descripción de una ley, proporciona una respuesta como "La ley número 26 establece que..." extrayendo la información relevante de los resultados obtenidos.
    - Si la pregunta del usuario solicitaba varios artículos de una ley, enuméralos y ofrece una descripción para cada uno, en caso de que aplique, por ejemplo: "El articulo <número> de la ley <número> establece que...". Extrae la información necesaria de los resultados obtenidos.
    - Si la respuesta no contiene información relevante, indica que no se encontraron resultados para la pregunta.
    - Si la respuesta contiene información incorrecta o incompleta, aclara la situación y proporciona una respuesta adecuada.
    - Si la respuesta tiene un contenido vacio o nulo, indica que no se encontraron resultados relacionados para la pregunta.

    **Genera únicamente la respuesta en español no en otro idioma** sin explicaciones ni comentarios adicionales.
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

    response = stream.choices[0].message.content
    print(f"\n\n-----------------------------------Model Response-----------------------------------\n\n{response}\n\n------------------------------------------------------------------------------------\n\n")

    return response

# Pregunta de prueba
question = "¿Que establece el articulo numero 12 de la ley 26?"
consult_knowledge_graph(question)