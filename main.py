from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from Part_1_Agent.agent import create_query
from Part_1_Agent.get_table import execute_northwind_query

app = FastAPI()
origins = [
    "http://localhost:3000",  # Example: Your frontend running on port 3000
    "http://127.0.0.1:3000",  # Example: Another way to access localhost
    "*",                      # Allows all origins (not recommended for production)
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_sql")
async def generate_sql(request: Request):
    data = await request.json()
    text_input = data.get('text_input', '')
    sql = await create_query(text_input)
    
    return {"sql": sql}

@app.post("/get_data")
async def get_data(request: Request):
    try:
        data = await request.json()
        sql = data.get("sql", "").lower()
        results = await execute_northwind_query(
            sql,
            as_dataframe=True
        )
        results_serializable = results.to_dict(orient="records")
        return {"status": "success", "data": results_serializable}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}