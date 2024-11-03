from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rdf_generator import generate_rdf
from decision_model import make_decision
from pydantic import BaseModel

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
    generate_rdf()
    return None

@app.post("/prompt")
def process_prompt(user_prompt : Prompt):
    prompt_type = make_decision(user_prompt.prompt)
    
    if(prompt_type == "Específica"):
        #Sent prompt to ask KG
        return "Especifica"
    elif(prompt_type == "Inferencial"):
        #sent prompt to the fine tuned model
        return "Inferencial"
    else:
        #sent prompt to the fine tuned model
        return "No se sabe"
    
    