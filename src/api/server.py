from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware
from src.api import carts, items, modifier, catalog

description = """
Fallen Stars -- for all your armory needs!
"""

app = FastAPI(
    title="Fallen Stars",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "James del Valle Irwin",
        "email": "jirwin06@calpoly.edu",
    },
)

# TODO: not sure if this is the right origin
origins = ["https://potion-exchange.vercel.app"]


app.include_router(items.router)
app.include_router(modifier.router)
app.include_router(carts.router)
app.include_router(catalog.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to Fallen Stars, THE premier armory"}