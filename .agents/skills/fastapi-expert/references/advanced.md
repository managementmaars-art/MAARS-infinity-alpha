# FastAPI Advanced Features

## Dependency Injection System

### Basic Dependencies

```python
from fastapi import Depends

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons
```

### Class-Based Dependencies

```python
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
    return {"params": commons}
```

### Dependency with Yield (Cleanup)

```python
def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def get_users(db: Database = Depends(get_db)):
    return db.get_all_users()
```

### Sub-Dependencies

```python
def query_extractor(q: str | None = None):
    return q

def query_or_default(query: str = Depends(query_extractor)):
    if query:
        return query
    return "default"

@app.get("/items/")
async def read_items(final_query: str = Depends(query_or_default)):
    return {"query": final_query}
```

### Dependencies at Router Level

```python
from fastapi import APIRouter

async def verify_token(x_token: str):
    if x_token != "secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")

router = APIRouter(dependencies=[Depends(verify_token)])

@router.get("/items/")
async def read_items():
    return [{"item": "Foo"}]
```

### Global Dependencies

```python
app = FastAPI(dependencies=[Depends(verify_api_key)])
```

## Middleware

### Custom HTTP Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Request Logging Middleware

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### GZip Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Trusted Host Middleware

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

## WebSocket Support

### Basic WebSocket

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")
```

### WebSocket with Authentication

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, token: str):
    # Verify token
    user = verify_token(token)
    if not user:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"User {client_id}: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
```

### WebSocket Connection Manager

```python
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left")
```

## Background Tasks

### Simple Background Task

```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as log:
        log.write(f"{message}\n")

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    return {"message": "Notification sent"}
```

### Multiple Background Tasks

```python
@app.post("/process/")
async def process_data(data: Data, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, data.email)
    background_tasks.add_task(update_database, data.id)
    background_tasks.add_task(notify_webhooks, data)
    return {"status": "Processing started"}
```

### Background Task with Dependencies

```python
def process_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    # Process order
    order.status = "completed"
    session.commit()

@app.post("/orders/")
async def create_order(order: Order, background_tasks: BackgroundTasks):
    # Save order
    save_order(order)

    # Process in background
    background_tasks.add_task(process_order, order.id)
    return {"status": "Order created"}
```

## Request and Response Models

### Request Body Validation

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=18, le=120)

@app.post("/users/")
async def create_user(user: UserCreate):
    return user
```

### Response Model

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    # Don't include password in response

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Save user with password
    saved_user = save_user(user)
    # Response automatically excludes password
    return saved_user
```

### Multiple Response Models

```python
from typing import Union

@app.get("/items/{item_id}", response_model=Union[Item, Error])
async def read_item(item_id: int):
    if item_id not in items_db:
        return Error(message="Item not found")
    return items_db[item_id]
```

### Response Model with Exclusions

```python
@app.get("/users/", response_model=List[User], response_model_exclude={"password"})
async def get_users():
    return users_db
```

## Advanced Response Types

### Streaming Response

```python
from fastapi.responses import StreamingResponse
import io

def generate_csv():
    data = io.StringIO()
    data.write("id,name,email\n")
    for user in users:
        data.write(f"{user.id},{user.name},{user.email}\n")
    data.seek(0)
    return data

@app.get("/export/users")
async def export_users():
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )
```

### File Response

```python
from fastapi.responses import FileResponse

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"files/{filename}"
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )
```

### Custom Response

```python
from fastapi.responses import Response

@app.get("/custom")
async def custom_response():
    content = "<h1>Custom HTML</h1>"
    return Response(content=content, media_type="text/html")
```

## Request Forms and Files

### Form Data

```python
from fastapi import Form

@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}
```

### File Upload

```python
from fastapi import File, UploadFile

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }
```

### Multiple File Upload

```python
@app.post("/uploadfiles/")
async def upload_files(files: List[UploadFile] = File()):
    return {
        "filenames": [file.filename for file in files]
    }
```

## Testing

### Test Client

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

### Testing with Database

```python
import pytest
from sqlmodel import create_engine, Session

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_user(session):
    user = User(name="Test", email="test@example.com")
    session.add(user)
    session.commit()

    assert user.id is not None
```

### Async Testing

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/items/")
    assert response.status_code == 200
```

## Event Handlers

### Startup Events

```python
@app.on_event("startup")
async def startup_event():
    # Initialize database
    create_db_and_tables()
    # Warm up cache
    await warm_cache()
    print("Application started")
```

### Shutdown Events

```python
@app.on_event("shutdown")
async def shutdown_event():
    # Close database connections
    await database.disconnect()
    # Clean up resources
    print("Application shutting down")
```

## Application Configuration

### Settings Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()

@app.get("/info")
async def info():
    return {"app_name": settings.app_name}
```

### Dependency Injection for Settings

```python
def get_settings():
    return Settings()

@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name}
```
