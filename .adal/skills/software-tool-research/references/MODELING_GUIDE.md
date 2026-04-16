# Architectural Modeling Guide

Techniques for creating accurate and useful architectural models from code analysis.

## Table of Contents
- [Component Diagrams](#component-diagrams)
- [Dependency Graphs](#dependency-graphs)
- [Sequence Diagrams](#sequence-diagrams)
- [Data Flow Diagrams](#data-flow-diagrams)
- [Class Diagrams](#class-diagrams)

## Component Diagrams

Visualize major system components and their relationships.

### When to Use
- High-level architecture overview
- Understanding component responsibilities
- Identifying coupling between components

### Mermaid Syntax

**Basic Component Diagram:**
```mermaid
graph TB
    UI[User Interface]
    API[API Layer]
    BL[Business Logic]
    DB[(Database)]
    
    UI --> API
    API --> BL
    BL --> DB
```

**With Multiple Connections:**
```mermaid
graph LR
    Client[Client App]
    Gateway[API Gateway]
    Auth[Auth Service]
    User[User Service]
    DB1[(Auth DB)]
    DB2[(User DB)]
    
    Client --> Gateway
    Gateway --> Auth
    Gateway --> User
    Auth --> DB1
    User --> DB2
    User -.->|verifies| Auth
```

**Styling for Clarity:**
```mermaid
graph TB
    subgraph "Frontend"
        UI[UI Components]
        State[State Management]
    end
    
    subgraph "Backend"
        API[REST API]
        Service[Business Services]
    end
    
    subgraph "Data"
        Cache[(Redis Cache)]
        DB[(PostgreSQL)]
    end
    
    UI --> State
    State --> API
    API --> Service
    Service --> Cache
    Service --> DB
    
    classDef frontend fill:#e1f5ff
    classDef backend fill:#fff4e1
    classDef data fill:#ffe1e1
    
    class UI,State frontend
    class API,Service backend
    class Cache,DB data
```

### Discovery Process

1. **Identify components:**
   - Use `list_dir` to see top-level structure
   - Look for logical groupings (folders, modules)
   - Read main entry points to find initialization

2. **Map relationships:**
   - Use `grep_search` for imports between components
   - Check for dependency injection configurations
   - Look at interface definitions

3. **Document responsibilities:**
   - Read README or inline comments
   - Examine main classes/functions in each component
   - Review tests to understand expected behavior

### Example Analysis Code

```markdown
## Component Discovery

### Step 1: List Structure
Components found:
- `src/frontend/` - UI code
- `src/api/` - REST endpoints
- `src/services/` - Business logic
- `src/models/` - Data structures
- `src/storage/` - Database access

### Step 2: Find Dependencies
```grep_search: "from src.services import"```
Results show API depends on services.

```grep_search: "from src.storage import"```
Results show services depend on storage.

### Step 3: Generate Diagram
[Mermaid diagram here]
```

## Dependency Graphs

Show how code modules depend on each other.

### When to Use
- Understanding coupling and cohesion
- Identifying circular dependencies
- Planning refactoring
- Analyzing impact of changes

### Visualization Options

**Table Format:**
| Module | Direct Dependencies | Dependents |
|--------|-------------------|------------|
| core | utils, config | services, api |
| services | core, models | api, cli |
| api | services, auth | - |
| models | core | services, storage |

**Tree Format:**
```
api/
├─ services/
│  ├─ core/
│  │  └─ utils/
│  └─ models/
│     └─ core/
└─ auth/
   └─ core/
```

**Graph Format:**
```mermaid
graph LR
    API --> Services
    API --> Auth
    Services --> Core
    Services --> Models
    Auth --> Core
    Models --> Core
    Core --> Utils
```

### Discovery Process

1. **Map imports:**
   - Use `grep_search` with patterns like `^import|^from`
   - For Python: look for `from X import Y`
   - For JavaScript: look for `import ... from`
   - For Java: look for `import` statements

2. **Identify external dependencies:**
   - Read package.json, requirements.txt, pom.xml
   - Separate standard library from third-party
   - Note version constraints

3. **Analyze depth:**
   - Count levels of dependency
   - Identify leaf nodes (no dependencies)
   - Find root nodes (many dependents)

### Detecting Issues

**Circular Dependencies:**
```mermaid
graph LR
    A --> B
    B --> C
    C --> A
    
    style A fill:#ffcccc
    style B fill:#ffcccc
    style C fill:#ffcccc
```
Look for import cycles that can cause initialization problems.

**Excessive Coupling:**
```mermaid
graph TB
    Core[Core Module]
    A[Module A] --> Core
    B[Module B] --> Core
    C[Module C] --> Core
    D[Module D] --> Core
    E[Module E] --> Core
    
    style Core fill:#ffcccc
```
A module with too many dependents may need splitting.

## Sequence Diagrams

Show interaction flow over time.

### When to Use
- Understanding request/response flow
- Documenting API workflows
- Debugging complex interactions
- Explaining initialization sequences

### Mermaid Syntax

**Basic Request Flow:**
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant DB
    
    Client->>API: POST /users
    API->>Service: create_user(data)
    Service->>DB: INSERT user
    DB-->>Service: user_id
    Service-->>API: User object
    API-->>Client: 201 Created
```

**With Error Handling:**
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Service
    
    Client->>API: GET /data
    API->>Auth: validate_token()
    
    alt token valid
        Auth-->>API: user_id
        API->>Service: get_data(user_id)
        Service-->>API: data
        API-->>Client: 200 OK
    else token invalid
        Auth-->>API: error
        API-->>Client: 401 Unauthorized
    end
```

**Async Operations:**
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Queue
    participant Worker
    participant DB
    
    Client->>API: POST /process
    API->>Queue: enqueue(task)
    API-->>Client: 202 Accepted (task_id)
    
    Queue->>Worker: task
    Worker->>DB: process()
    Worker->>DB: update_status()
    
    Note over Client,DB: Client polls for status
    Client->>API: GET /status/task_id
    API->>DB: get_status()
    DB-->>API: status
    API-->>Client: status
```

### Discovery Process

1. **Identify entry point:**
   - Find main function or route handler
   - Read API documentation or route definitions

2. **Trace execution:**
   - Follow function calls through code
   - Note async/await or callbacks
   - Check for error handling paths

3. **Document interactions:**
   - List participants (objects, services)
   - Note message types (sync, async, return)
   - Capture alternative flows (errors, conditionals)

## Data Flow Diagrams

Show how data moves through the system.

### When to Use
- Understanding data transformations
- Documenting ETL processes
- Analyzing pipeline architectures
- Planning data governance

### Notation

**Simple Flow:**
```mermaid
graph LR
    Input[Raw Data] --> Parse[Parser]
    Parse --> Validate[Validator]
    Validate --> Transform[Transformer]
    Transform --> Output[Processed Data]
```

**With Branching:**
```mermaid
graph TB
    Input[Input Data]
    Process{Valid?}
    Success[Process Data]
    Error[Error Handler]
    Output[Output]
    Log[Error Log]
    
    Input --> Process
    Process -->|Yes| Success
    Process -->|No| Error
    Success --> Output
    Error --> Log
```

**Multi-stage Pipeline:**
```mermaid
graph LR
    subgraph "Stage 1: Ingestion"
        A[Source] --> B[Collector]
    end
    
    subgraph "Stage 2: Processing"
        B --> C[Validator]
        C --> D[Transformer]
    end
    
    subgraph "Stage 3: Storage"
        D --> E[Aggregator]
        E --> F[(Database)]
    end
```

### Discovery Process

1. **Identify data sources:**
   - Files, databases, APIs, user input
   - Read configuration for data connections

2. **Trace transformations:**
   - Look for functions that modify data
   - Check for validation, parsing, mapping
   - Note where data format changes

3. **Find data sinks:**
   - Where data is written/output
   - Storage locations, APIs, files

## Class Diagrams

Show object-oriented structure and relationships.

### When to Use
- Understanding OOP design
- Documenting domain models
- Analyzing inheritance hierarchies
- Planning refactoring of class structure

### Mermaid Syntax

**Basic Class Structure:**
```mermaid
classDiagram
    class User {
        +String username
        +String email
        +DateTime created_at
        +login()
        +logout()
        +update_profile()
    }
    
    class Admin {
        +String[] permissions
        +delete_user()
        +grant_permission()
    }
    
    class Post {
        +String title
        +String content
        +DateTime published_at
        +publish()
        +archive()
    }
    
    User <|-- Admin
    User "1" --> "*" Post : creates
```

**With Interfaces:**
```mermaid
classDiagram
    class Authenticator {
        <<interface>>
        +authenticate(credentials)
        +validate_token(token)
    }
    
    class JWTAuthenticator {
        +secret_key
        +authenticate(credentials)
        +validate_token(token)
        -generate_token()
    }
    
    class OAuth2Authenticator {
        +provider
        +client_id
        +authenticate(credentials)
        +validate_token(token)
        -exchange_code()
    }
    
    Authenticator <|.. JWTAuthenticator
    Authenticator <|.. OAuth2Authenticator
```

### Discovery Process

1. **Find class definitions:**
   - Use `grep_search` for `class ` pattern
   - Look in models/, domain/, entities/

2. **Extract attributes and methods:**
   - Read class definitions
   - Note public vs private members
   - Identify class vs instance methods

3. **Map relationships:**
   - Inheritance: `class Child(Parent)`
   - Composition: Class has instance of another
   - Association: Class references another

## Best Practices

### Choosing the Right Diagram

- **Component**: High-level system overview
- **Dependency**: Module coupling analysis
- **Sequence**: Request flow and interactions
- **Data Flow**: Data transformation pipeline
- **Class**: Object-oriented domain modeling

### Diagram Complexity

**Keep diagrams focused:**
- One diagram per concept/workflow
- Maximum 7-10 elements per diagram
- Use subgraphs to group related items
- Create multiple views for complex systems

**Progressive disclosure:**
1. High-level overview diagram
2. Detailed diagrams for each component
3. Code-level diagrams for complex parts

### Validation

**Verify accuracy:**
- Cross-reference with code
- Test understanding by tracing execution
- Review with generated tests in mind
- Check against documentation

**Keep updated:**
- Note analysis date
- Link to specific commit/version
- Mark as "snapshot" not "specification"

## Tools Integration

### Using Copilot Tools

**For Component Discovery:**
```
1. list_dir("/path/to/project")
2. semantic_search("component initialization")
3. read_file for main entry points
4. grep_search for import patterns
```

**For Dependency Mapping:**
```
1. grep_search("^from |^import ", isRegexp=true)
2. read package.json/requirements.txt
3. list_code_usages for specific classes
```

**For Sequence Tracing:**
```
1. semantic_search("API endpoint handler")
2. read_file for route definitions
3. Follow function calls with read_file
4. Check tests for expected flow
```

### Code Markers to Look For

**Architecture clues:**
- `__init__.py` files (Python package structure)
- `index.ts` exports (JavaScript module structure)
- `@Injectable`, `@Component` (Dependency injection)
- `interface`, `abstract class` (Contracts)

**Relationship clues:**
- Import statements (dependencies)
- Constructor parameters (composition)
- Base class in definition (inheritance)
- Callback/event registration (pub-sub)
