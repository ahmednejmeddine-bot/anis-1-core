from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

class Task(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"ANIS-1": "AI Super Team Backend Running"}

@app.post("/run-agent")
def run_agent(task: Task):
    # Placeholder for AI agent execution
    return {
        "status": "Agent received task",
        "task": task.prompt
    }
