# Architectural Patterns Reference

Common architectural patterns found in software tools and how to identify them.

## Table of Contents
- [Layered Architecture](#layered-architecture)
- [Microservices](#microservices)
- [Plugin Architecture](#plugin-architecture)
- [MVC/MVT/MVVM](#mvcmvtmvvm)
- [Event-Driven](#event-driven)
- [Client-Server](#client-server)
- [Pipeline Architecture](#pipeline-architecture)

## Layered Architecture

**Identification signals:**
- Folders named: `presentation/`, `business/`, `data/`, `core/`
- Imports flow in one direction (top layers depend on bottom)
- Clear separation of concerns

**Common in:**
- Enterprise applications
- Web backends
- Business software

**Example structure:**
```
app/
├── presentation/    # UI, controllers, routes
├── business/        # Business logic, services
├── data/           # Database, repositories
└── infrastructure/ # Config, utilities
```

**Documentation pattern:**
```markdown
## Layered Architecture

### Presentation Layer
- Handles HTTP requests/responses
- Input validation
- View rendering

### Business Layer
- Core business logic
- Domain rules
- Workflow orchestration

### Data Layer
- Database access
- Data persistence
- Query building
```

## Microservices

**Identification signals:**
- Multiple deployable units
- `docker-compose.yml` with multiple services
- Service discovery configuration
- API gateways
- Independent databases per service

**Common in:**
- Distributed systems
- Cloud-native applications
- Scalable platforms

**Example structure:**
```
project/
├── auth-service/
├── user-service/
├── payment-service/
├── api-gateway/
└── docker-compose.yml
```

**Documentation pattern:**
```markdown
## Microservices Architecture

### Services
1. **Auth Service** (Port 8001)
   - User authentication
   - Token generation
   
2. **User Service** (Port 8002)
   - User profile management
   - CRUD operations

### Communication
- REST APIs between services
- Message queue for async operations
- Service mesh: [Technology]
```

## Plugin Architecture

**Identification signals:**
- `plugins/` or `extensions/` directory
- Plugin interface or base class
- Plugin registry/loader
- Configuration for enabling plugins

**Common in:**
- Extensible applications
- Development tools
- Content management systems

**Example structure:**
```
app/
├── core/
├── plugins/
│   ├── plugin_a/
│   ├── plugin_b/
│   └── plugin_interface.py
└── plugin_loader.py
```

**Documentation pattern:**
```markdown
## Plugin Architecture

### Plugin Interface
- `initialize()` - Setup plugin
- `process(data)` - Main operation
- `cleanup()` - Teardown

### Plugin Discovery
- Scans `plugins/` directory
- Loads based on `plugin.yaml` config
- Validates plugin interface compliance

### Example Plugin
[code showing plugin implementation]
```

## MVC/MVT/MVVM

**Identification signals:**
- Folders: `models/`, `views/`, `controllers/` (or similar)
- Template files
- Routes that connect URLs to controllers
- Data models with business logic

**Common in:**
- Web frameworks (Django, Rails, Spring)
- Desktop applications
- Mobile apps

**MVC Example:**
```
app/
├── models/        # Data structures
├── views/         # Templates
├── controllers/   # Request handlers
└── routes.py
```

**Documentation pattern:**
```markdown
## MVC Pattern

### Models
- User: Authentication, profile data
- Post: Content, metadata
- Comment: User feedback

### Views
- Templates for rendering
- Data presentation logic

### Controllers
- UserController: Registration, login
- PostController: CRUD operations
```

## Event-Driven

**Identification signals:**
- Event bus or message broker (Kafka, RabbitMQ, Redis)
- Event handlers/listeners
- Pub-sub patterns
- Event sourcing

**Common in:**
- Real-time systems
- Reactive applications
- Distributed systems

**Example structure:**
```
app/
├── events/
│   ├── user_events.py
│   └── order_events.py
├── handlers/
│   ├── email_handler.py
│   └── notification_handler.py
└── event_bus.py
```

**Documentation pattern:**
```markdown
## Event-Driven Architecture

### Events
- `UserRegistered`: Fired on new user signup
- `OrderPlaced`: Fired on order creation

### Handlers
- EmailHandler: Sends welcome emails
- NotificationHandler: Pushes notifications

### Event Flow
1. User action triggers event
2. Event published to bus
3. Subscribed handlers process event
4. Side effects executed asynchronously
```

## Client-Server

**Identification signals:**
- Separate `client/` and `server/` directories
- API definitions (REST, GraphQL, gRPC)
- Frontend and backend technologies
- Network communication code

**Common in:**
- Web applications
- Mobile apps with backend
- Distributed applications

**Example structure:**
```
project/
├── client/         # Frontend (React, Vue, etc.)
├── server/         # Backend (Node, Python, etc.)
└── shared/         # Common code
```

**Documentation pattern:**
```markdown
## Client-Server Architecture

### Client
- Technology: React
- State management: Redux
- API client: Axios

### Server
- Technology: Express.js
- Database: PostgreSQL
- Authentication: JWT

### Communication
- Protocol: REST over HTTPS
- Data format: JSON
- Authentication: Bearer token
```

## Pipeline Architecture

**Identification signals:**
- Sequential processing stages
- Filters or transformers
- Data flows through pipeline
- Each stage has specific responsibility

**Common in:**
- Data processing tools
- Build systems
- Stream processing

**Example structure:**
```
app/
├── stages/
│   ├── input.py
│   ├── transform.py
│   ├── validate.py
│   └── output.py
└── pipeline.py
```

**Documentation pattern:**
```markdown
## Pipeline Architecture

### Stages
1. **Input**: Read data from source
2. **Parse**: Convert format
3. **Transform**: Apply business logic
4. **Validate**: Check constraints
5. **Output**: Write results

### Data Flow
Input → Parse → Transform → Validate → Output

### Example
[code showing pipeline execution]
```

## Identifying Mixed Patterns

Many real-world systems combine multiple patterns:

**Example: Web application with plugins**
- MVC for web framework
- Plugin architecture for extensibility
- Layered architecture within each plugin

**How to document:**
```markdown
## Hybrid Architecture

### Primary Pattern: MVC
- Web framework structure
- Route → Controller → Model → View

### Secondary Pattern: Plugin System
- Plugins extend core functionality
- Each plugin follows MVC internally

### Integration
- Plugins register routes with main app
- Plugins can override core views
- Plugin models extend core models
```

## Analysis Checklist

When identifying architecture:

- [ ] What is the primary decomposition? (By layer, feature, service)
- [ ] How are responsibilities separated?
- [ ] What patterns are evident in folder structure?
- [ ] How do components communicate?
- [ ] Are there configuration files that reveal architecture?
- [ ] Do tests reveal architectural boundaries?
- [ ] Does documentation explicitly name the pattern?
