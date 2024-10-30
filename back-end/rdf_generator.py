import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL
import sqlalchemy
from sqlalchemy import MetaData, inspect
import json
from DB import get_database_schema
from dotenv import load_dotenv
import os

load_dotenv()

def generate_rdf(output_path="output.rdf"):
    # Load the database URL from environment variables
    db_url = os.getenv('DATABASE_URL')
    engine = sqlalchemy.create_engine(db_url)

    # Reflect the database schema
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Create an inspector to get foreign keys
    inspector = inspect(engine)
    knowledge_graph = Graph()

    # Define namespaces
    KG_NS = Namespace("http://www.semanticweb.org/KG#")
    knowledge_graph.bind("knowledge_graph", KG_NS)
    knowledge_graph.bind("rdf", RDF)
    knowledge_graph.bind("owl", OWL)
    knowledge_graph.bind("rdfs", RDFS)


    # Get the database schema as a dictionary
    schema = get_database_schema()
    schema_dict = json.loads(schema)
    #print(json.dumps(schema_dict, indent=4))

    # Add classes and properties to the knowledge graph based on the schema
    for table_name, table_info in schema_dict.items():
        knowledge_graph.add((KG_NS[table_name], RDF.type, OWL.Class))

        for column in table_info['columns']:

            column_name = column['COLUMN_NAME']
            data_type = "string" if column['DATA_TYPE'] == "varchar" else column['DATA_TYPE']
            property_uri = f"{KG_NS[column_name]}_{table_name}"

            knowledge_graph.add((URIRef(property_uri), RDF.type, OWL.DatatypeProperty))
            knowledge_graph.add((URIRef(property_uri), RDFS.domain, KG_NS[table_name]))
            knowledge_graph.add((URIRef(property_uri), RDFS.range, XSD[data_type]))

    # Add instances to the knowledge graph based on the data in the database
    for table in metadata.tables.keys():
        df = pd.read_sql_table(table, engine)
        foreign_keys = inspector.get_foreign_keys(table)

        # Add properties for foreign keys
        for fk in foreign_keys:
            for constrain in fk['constrained_columns']:
                ref_table = fk['referred_table']
                knowledge_graph.add((KG_NS[f"fk_{constrain}"], RDF.type, OWL.ObjectProperty))
                knowledge_graph.add((KG_NS[f"fk_{constrain}"], RDFS.domain, KG_NS[table]))
                knowledge_graph.add((KG_NS[f"fk_{constrain}"], RDFS.range, KG_NS[ref_table]))

        for _, row in df.iterrows():
            # Create a subject URI for each row in the table
            subject = KG_NS[f"{table}_{row.iloc[0]}"]
            pk_row = row.iloc[0]
            description = row.iloc[1]

            # Add the subject as an instance of OWL.NamedIndividual and the table class
            knowledge_graph.add((subject, RDF.type, OWL.NamedIndividual))
            knowledge_graph.add((subject, RDF.type, KG_NS[table]))

            # Add properties for the primary key and description
            knowledge_graph.add((subject, KG_NS[f"{row.index[1]}_{table}"], Literal(description)))
            knowledge_graph.add((subject, KG_NS[f"{row.index[0]}_{table}"], Literal(pk_row)))

            # Add foreign key relationships for the "articulo" table
            if table == "articulo":
                knowledge_graph.add((subject, KG_NS[f"fk_{constrain}"], KG_NS[f"ley_{row.iloc[2]}"]))

    # Serialize the knowledge graph to a XML file
    knowledge_graph.serialize(destination=output_path, format="pretty-xml")
    return output_path