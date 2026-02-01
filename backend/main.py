from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import json
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later we restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CUSTOMER_DB = r'C:\Users\Dell\Desktop\Resolvex_FastAPI\database\database_customer.json'
AGENT_DB = r'C:\Users\Dell\Desktop\Resolvex_FastAPI\database\database_agent.json'
TICKET_DB = r'C:\Users\Dell\Desktop\Resolvex_FastAPI\database\database_ticket.json'


# ------------------ Utility Functions ------------------

def load_data(file_path):
    if not Path(file_path).exists():
        return []
    with open(file_path, "r") as f:
        return json.load(f)


def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def generate_customer_id(customers):
    if not customers:
        return "CUST-1001"
    last_id = customers[-1]["id"]
    number = int(last_id.split("-")[1]) + 1
    return f"CUST-{number}"

def generate_agent_id(agents):
    if not agents:
        return "AGT-2001"
    last_id = agents[-1]["id"]
    number = int(last_id.split("-")[1]) + 1
    return f"AGT-{number}"


# ------------------ Pydantic Models ------------------

class CustomerSignup(BaseModel):
    name: str
    department: str
    email: EmailStr
    password: str


class AgentSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginModel(BaseModel):
    email: EmailStr
    password: str

class Ticket(BaseModel):
    title: str
    description: str
    priority: str
    created_by: str




# ------------------ Signup Endpoints ------------------

@app.post("/signup/customer")
def signup_customer(user: CustomerSignup):
    customers = load_data(CUSTOMER_DB)

    for c in customers:
        if c["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    new_id = generate_customer_id(customers)

    new_customer = {
        "id": new_id,
        "name": user.name,
        "department": user.department,
        "email": user.email,
        "password": user.password
    }

    customers.append(new_customer)
    save_data(CUSTOMER_DB, customers)

    return {"message": "Customer registered successfully"}


# =========================
# 📝 AGENT SIGNUP
# =========================
@app.post("/signup/agent")
def signup_agent(user: AgentSignup):
    agents = load_data(AGENT_DB)

    for a in agents:
        if a["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    new_id = generate_agent_id(agents)

    new_agent = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
        "password": user.password
    }

    agents.append(new_agent)
    save_data(AGENT_DB, agents)

    return {"message": "Agent registered successfully"}
# ------------------ Login Endpoints ------------------

@app.post("/login/customer")
def login_customer(login_data: LoginModel):
    data = load_data(CUSTOMER_DB)

    for user in data:
        if user["email"] == login_data.email and user["password"] == login_data.password:
            return {"message": "Customer login successful", "user_id": user["id"],"role": "customer"}

    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.post("/login/agent")
def login_agent(login_data: LoginModel):
    data = load_data(AGENT_DB)

    for user in data:
        if user["email"] == login_data.email and user["password"] == login_data.password:
            return {"message": "Agent login successful", "user_id": user["id"],"role": "agent"}

    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.get("/tickets")
def get_all_tickets():
    tickets = load_data(TICKET_DB)
    return tickets


@app.post("/create-ticket")
def create_ticket(ticket: Ticket):
    tickets = load_data(TICKET_DB)

    ticket_id = f"TICK{len(tickets)+1:03d}"

    new_ticket = {
        "ticket_id": ticket_id,
        "title": ticket.title,
        "description": ticket.description,
        "priority": ticket.priority,
        "status": "Open",
        "created_by": ticket.created_by,
        "assigned_to": "Not Assigned",
        "date": datetime.now().strftime("%d-%m-%Y")
    }

    tickets.append(new_ticket)
    save_data(TICKET_DB, tickets)

    return {"message": "Ticket created"}


@app.get("/tickets/agent/{agent_id}")
def get_agent_tickets(agent_id: str):
    tickets = load_data(TICKET_DB)
    agent_tickets = [t for t in tickets if t["assigned_to"] == agent_id]
    return agent_tickets


@app.get("/customers")
def get_customers():
    return load_data(CUSTOMER_DB)

@app.get("/agents")
def get_agents():
    return load_data(AGENT_DB)

@app.delete("/delete-customer/{email}")
def delete_customer(email: str):
    customers = load_data(CUSTOMER_DB)
    customers = [c for c in customers if c["email"] != email]
    save_data(CUSTOMER_DB, customers)
    return {"message": "Customer deleted"}

@app.delete("/delete-agent/{email}")
def delete_agent(email: str):
    agents = load_data(AGENT_DB)
    agents = [a for a in agents if a["email"] != email]
    save_data(AGENT_DB, agents)
    return {"message": "Agent deleted"}

@app.delete("/delete-ticket/{ticket_id}")
def delete_ticket(ticket_id: str):
    tickets = load_data(TICKET_DB)
    tickets = [t for t in tickets if str(t["ticket_id"]) != str(ticket_id)]
    save_data(TICKET_DB, tickets)
    return {"message": "Ticket deleted"}

