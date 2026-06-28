from fastapi import Depends, HTTPException, Request

API_KEY = "flocker-challenge-key-2024"


def verify_api_key(request: Request) -> None:
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
