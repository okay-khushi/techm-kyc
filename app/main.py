from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.middleware import RequestLoggingMiddleware
from app.api.routes import router
from app.exceptions.agent_exception import AgentExecutionError
from app.exceptions.guardrail_exception import GuardrailViolationError
from app.exceptions.validation_exception import RequestValidationError

app = FastAPI(
    title="AI Orchestration Engine",
    version="1.0"
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(router)

# Self-contained dashboard: submits contracts/SOWs to /api/v1/analyze*
# and renders the resulting pipeline state + SAR report. No build step,
# no extra dependencies — served straight from app/static/dashboard.
app.mount(
    "/dashboard",
    StaticFiles(directory="app/static/dashboard", html=True),
    name="dashboard",
)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(GuardrailViolationError)
async def guardrail_violation_handler(request: Request, exc: GuardrailViolationError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(AgentExecutionError)
async def agent_execution_handler(request: Request, exc: AgentExecutionError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/")
async def root():
    return {"message": "AI Orchestration Engine Running"}


@app.get("/health")
async def health():
    return {"status": "ok"}