#!/usr/bin/env python3
"""Script to register a default user for MAARS Command."""
import asyncio
import httpx
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

async def register_user():
    user_data = UserCreate(
        email="admin@maars.com",
        name="MAARS Admin",
        password="password123"
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/auth/register",
                json=user_data.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print("User registered successfully!")
                print("Email: admin@maars.com")
                print("Password: password123")
                print("Response:", response.json())
            else:
                print(f"Registration failed: {response.status_code}")
                print("Response:", response.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(register_user())