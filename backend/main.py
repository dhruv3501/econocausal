from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File, Form
import pandas as pd
import io
app = FastAPI(title="EconoCausal Backend")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="EconoCausal Backend - Swagger",
        swagger_css_url="/static/swagger-mint.css"
    )
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def home():
    return {"message": "EconoCausal backend is running"}
@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    budget: float = Form(...)
):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    df = df.sort_values("estimated_ite", ascending=False)
    high_budget = budget * 0.60
    medium_budget = budget * 0.30
    low_budget = budget * 0.10
    # Check required column
    if "estimated_ite" not in df.columns:
        return {
            "message": "CSV must contain an estimated_ite column"
        }
    # Sort customers by estimated treatment effect
    df = df.sort_values(
        by="estimated_ite",
        ascending=False
    ).reset_index(drop=True)
    # Divide customers into three groups
    total_customers = len(df)
    high_end = int(total_customers * 0.20)
    medium_end = int(total_customers * 0.50)
    high_uplift = df.iloc[:high_end]
    medium_uplift = df.iloc[high_end:medium_end]
    low_uplift = df.iloc[medium_end:]
    return {
        "message": "Campaign analysis completed successfully",
        "total_customers": total_customers,
        "budget": budget,
        "high_uplift": {
            "customers": len(high_uplift),
            "budget": round(high_budget, 2),
            "average_ite": round(
                high_uplift["estimated_ite"].mean(), 2
            )
        },
        "medium_uplift": {
            "customers": len(medium_uplift),
            "budget": round(medium_budget, 2),
            "average_ite": round(
                medium_uplift["estimated_ite"].mean(), 2
            )
        },
        "low_uplift": {
            "customers": len(low_uplift),
            "budget": round(low_budget, 2),
            "average_ite": round(
                low_uplift["estimated_ite"].mean(), 2
            )
        }
    }