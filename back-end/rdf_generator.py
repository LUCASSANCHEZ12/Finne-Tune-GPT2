import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD
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
    knowledge_graph.bind("ley", KG_NS)
    knowledge_graph.bind("rdf", RDF)
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
        knowledge_graph.add((KG_NS[table_name], RDF.type, RDFS.Class))
        knowledge_graph.add((KG_NS[table_name], RDFS.label, Literal(table_name, datatype=XSD.string)))

        for column in table_info['columns']:
            column_name = column['COLUMN_NAME']
            data_type = column['DATA_TYPE']
            property_uri = KG_NS[column_name]
            knowledge_graph.add((property_uri, RDF.type, RDF.Property))
            knowledge_graph.add((property_uri, RDFS.label, Literal(column_name, datatype=XSD.string)))
            knowledge_graph.add((property_uri, RDFS.range, Literal(data_type, datatype=XSD.string)))

    # Add instances to the knowledge graph based on the data in the database
    for table in metadata.tables.keys():
        df = pd.read_sql_table(table, engine)
        foreign_keys = inspector.get_foreign_keys(table)

        for _, row in df.iterrows():
            subject = URIRef(KG_NS[f"{table}/{row.iloc[0]}"])
            knowledge_graph.add((subject, RDF.type, KG_NS[table]))

            label = generate_label(row)
            knowledge_graph.add((subject, RDFS.label, Literal(label, datatype=XSD.string)))

            for column in df.columns:
                value = row[column]
                if column in [fk['constrained_columns'][0] for fk in foreign_keys]:
                    ref_table = [fk['referred_table'] for fk in foreign_keys if fk['constrained_columns'][0] == column][0]
                    ref_subject = URIRef(KG_NS[f"{ref_table}/{value}"])
                    knowledge_graph.add((subject, KG_NS[f"has_{ref_table}"], ref_subject))
                else:
                    if isinstance(value, str):
                        knowledge_graph.add((subject, KG_NS[column], Literal(value, datatype=XSD.string)))
                    elif isinstance(value, (int, float)):
                        knowledge_graph.add((subject, KG_NS[column], Literal(value, datatype=XSD.double)))
                    else:
                        knowledge_graph.add((subject, KG_NS[column], Literal(str(value), datatype=XSD.string)))

    # Serialize the knowledge graph to a Turtle file
    knowledge_graph.serialize(destination=output_path, format="xml")
    return output_path