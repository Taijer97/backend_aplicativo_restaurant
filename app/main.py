import uvicorn, os, secrets
from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from db.base import engine, Base
from core.security import role_required
# módulo main.py (ajustes de import y registro de router)
from routers import auth, menu, tables, orders, reservations, ws_orders, user, category, sub_category, ws_menu
from fastapi.openapi.utils import get_openapi


app = FastAPI(
    title="Restaurant API Async + Auth + Roles + WS",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# ====== MODELOS ======
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_models()

# ====== RUTAS ======
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(sub_category.router)
app.include_router(menu.router)
app.include_router(tables.router)
app.include_router(orders.router)
app.include_router(reservations.router)
app.include_router(ws_orders.router)
app.include_router(ws_menu.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Restaurant Async API with WebSocket running"}

# ====== PROTECCIÓN DE DOCS ======
PROTECT_DOCS = os.getenv("PROTECT_DOCS", "false").lower() == "true"
DOCS_AUTH_MODE = os.getenv("DOCS_AUTH_MODE", "token").lower()
DOCS_ROLE_ID = int(os.getenv("DOCS_ROLE_ID", "1"))
DOCS_USER = os.getenv("DOCS_USER")
DOCS_PASS = os.getenv("DOCS_PASS")

basic_scheme = HTTPBasic()

async def docs_basic(credentials: HTTPBasicCredentials = Depends(basic_scheme)):
    if not DOCS_USER or not DOCS_PASS:
        raise HTTPException(status_code=401, detail="Docs basic auth not configured", headers={"WWW-Authenticate": "Basic"})
    if not (secrets.compare_digest(credentials.username, DOCS_USER) and secrets.compare_digest(credentials.password, DOCS_PASS)):
        raise HTTPException(status_code=401, detail="Invalid docs credentials", headers={"WWW-Authenticate": "Basic"})

deps = []
if PROTECT_DOCS:
    if DOCS_AUTH_MODE == "basic":
        deps = [Depends(docs_basic)]
    else:
        deps = [Depends(role_required([DOCS_ROLE_ID]))]

@app.get("/docs", include_in_schema=False, dependencies=deps)
async def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

@app.get("/redoc", include_in_schema=False, dependencies=deps)
async def custom_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="API ReDoc")

@app.get("/openapi.json", include_in_schema=False, dependencies=deps)
async def openapi():
    return JSONResponse(app.openapi())

# ====== TOKEN BEARER PARA AUTHORIZE ======
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="Restaurant Async API with Auth + Roles + WS",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
