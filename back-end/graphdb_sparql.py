from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:7200/repositories/Proyecto_KG_1")
sparql.setQuery("""
    PREFIX kg: <http://www.semanticweb.org/KG#>

    SELECT ?articulo ?num_articulo ?desc_art ?desc_ley ?num_ley

    WHERE {
        ?articulo a kg:articulo ;
            kg:Num_Articulo_articulo ?num_articulo ;
            kg:Descripcion_articulo ?desc_art ;
            kg:fk_Num_ley ?ley .
        ?ley kg:Descripcion_ley ?desc_ley;
            kg:Num_Ley_ley ?num_ley .
            
    }
""")
sparql.setReturnFormat(JSON)

results = sparql.query().convert()
print(results)

