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
    KG_NS = Namespace("http://example.org/KG/")
    knowledge_graph.bind("knowledge_graph", KG_NS)
    knowledge_graph.bind("rdf", RDF)
    knowledge_graph.bind("owl", OWL)
    knowledge_graph.bind("rdfs", RDFS)

    # Helper function to generate labels for resources
    def generate_label(row):
        if len(row) > 1:  
            return str(row.iloc[1]) 
        return f"Resource {row.iloc[0]}"

    # Get the database schema as a dictionary
    schema = get_database_schema()
    schema_dict = json.loads(schema)
    print(json.dumps(schema_dict, indent=4))

    # Add classes and properties to the knowledge graph based on the schema
    for table_name, table_info in schema_dict.items():
        knowledge_graph.add((KG_NS[table_name], RDF.type, OWL.Class))
        knowledge_graph.add((KG_NS[table_name], RDFS.label, Literal(table_name, datatype=XSD.string)))

        for column in table_info['columns']:
            column_name = column['COLUMN_NAME']
            data_type = column['DATA_TYPE']
            property_uri = KG_NS[column_name]
            knowledge_graph.add((property_uri, RDF.type, OWL.DatatypeProperty))
            knowledge_graph.add((property_uri, RDFS.label, Literal(column_name, datatype=XSD.string)))
            knowledge_graph.add((property_uri, RDFS.range, Literal(data_type, datatype=XSD.string)))

    # Add instances to the knowledge graph based on the data in the database
    for table in metadata.tables.keys():
        print(f"Processing table: {table}")
        df = pd.read_sql_table(table, engine)
        foreign_keys = inspector.get_foreign_keys(table)
        print(foreign_keys)

        # Add properties for foreign keys
        for fk in foreign_keys:
            for constrain in fk['constrained_columns']:
                ref_table = fk['referred_table']
                knowledge_graph.add((KG_NS[f"has_{constrain}"], RDF.type, OWL.ObjectProperty))
                knowledge_graph.add((KG_NS[f"has_{constrain}"], RDFS.domain, KG_NS[table]))
                knowledge_graph.add((KG_NS[f"has_{constrain}"], RDFS.range, KG_NS[ref_table]))

        for _, row in df.iterrows():
            subject = URIRef(KG_NS[f"{table}/{row.iloc[0]}"])
            knowledge_graph.add((subject, RDF.type, KG_NS[table]))

            label = generate_label(row)
            knowledge_graph.add((subject, RDFS.label, Literal(label, datatype=XSD.string)))

    # Serialize the knowledge graph to a XML file
    knowledge_graph.serialize(destination=output_path, format="pretty-xml")
    return output_path