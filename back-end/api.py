from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
#from rdf_generator import generate_rdf
from decision_model import make_decision
from model_for_huggingFace import consult_knowledge_graph
from pydantic import BaseModel
import uvicorn
import re
import sys
import os

ruta_model = os.path.join(os.path.dirname(__file__), './../Model')
sys.path.append(ruta_model)

from model_answer import ModelResponse

app = FastAPI()

origins = [
    'http://localhost'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

@app.get("/")
def create_rdf():
    #generate_rdf()
    return None

@app.post("/prompt")
def process_prompt(user_prompt : Prompt):
    prompt_type = make_decision(user_prompt.prompt)
    pattern = r"Específica\.?"
    matches = re.search(pattern, prompt_type, re.DOTALL)
    
    print(prompt_type)
    if(matches):
        #Sent prompt to ask KG
        try:
            response = consult_knowledge_graph(user_prompt.prompt)
            return JSONResponse(content={"response" : response})
        except Exception as e:
            print(f"ValueError: {e}")
            return JSONResponse(content={"error" : str(e)}) #Sent an error message
    else:
        #sent prompt to the fine tuned model in both cases
        try:
            response = ModelResponse(user_prompt.prompt)
            return JSONResponse(content={"response" : response})
        except Exception as e:
            print(f"ValueError: {str(e)}")
            return JSONResponse(content={"error" : str(e)}) #Sent an error message
        
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)