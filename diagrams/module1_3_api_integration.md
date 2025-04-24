# Module 1-3: Basic API Integration Flow

This diagram illustrates the flow of data and interactions in the basic API integration modules (1-3).

## Sequence Diagram for Basic API Call (Module 1)

```mermaid
sequenceDiagram
    participant User
    participant Module1 as Module 1 (Basic Client)
    participant GroqAPI as Groq API

    User->>Module1: Provide prompt
    Module1->>Module1: Load API key from .env
    Module1->>GroqAPI: Send POST request with prompt
    GroqAPI-->>Module1: Return response
    Module1-->>User: Display response
```

## Sequence Diagram for Conversation Client (Module 2)

```mermaid
sequenceDiagram
    participant User
    participant Module2 as Module 2 (Conversation Client)
    participant GroqAPI as Groq API

    User->>Module2: Initialize GroqChatbot
    Module2->>Module2: Set up conversation history

    loop Conversation
        User->>Module2: Send message
        Module2->>Module2: Add user message to history
        Module2->>GroqAPI: Send conversation history
        GroqAPI-->>Module2: Return response
        Module2->>Module2: Add assistant response to history
        Module2-->>User: Display response
    end

    alt Clear History
        User->>Module2: Request to clear history
        Module2->>Module2: Reset conversation history
        Module2-->>User: Confirm history cleared
    end

    alt Change Model
        User->>Module2: Request to change model
        Module2->>Module2: Update model setting
        Module2-->>User: Confirm model changed
    end
```

## API Server Architecture (Module 3)

```mermaid
graph TD
    subgraph "Flask API Server"
        API[Flask App]
        Routes[API Routes]
        ConversationStore[Conversation Store]
    end

    subgraph "API Routes"
        ChatEndpoint["API: /api/chat"]
        ClearEndpoint["API: /api/clear"]
        ModelsEndpoint["API: /api/models"]
        SessionsEndpoint["API: /api/sessions"]
    end

    subgraph "External"
        Client[Client Applications]
        GroqAPI[Groq API]
    end

    Client -->|HTTP Requests| API
    API -->|Route Handling| Routes
    Routes -->|Chat Request| ChatEndpoint
    Routes -->|Clear History| ClearEndpoint
    Routes -->|Get Models| ModelsEndpoint
    Routes -->|Get Sessions| SessionsEndpoint

    ChatEndpoint -->|Store| ConversationStore
    ChatEndpoint -->|API Call| GroqAPI
    ClearEndpoint -->|Clear| ConversationStore
    SessionsEndpoint -->|Read| ConversationStore

    GroqAPI -->|Response| ChatEndpoint
    ChatEndpoint -->|Response| Client
    ClearEndpoint -->|Response| Client
    ModelsEndpoint -->|Response| Client
    SessionsEndpoint -->|Response| Client

    classDef endpoint fill:#f96,stroke:#333,stroke-width:1px;
    class ChatEndpoint,ClearEndpoint,ModelsEndpoint,SessionsEndpoint endpoint;
```

## Data Flow Diagram

```mermaid
flowchart TD
    User([User]) -->|Input Prompt| Module1[Module 1\nBasic Client]
    Module1 -->|API Request| GroqAPI[Groq API]
    GroqAPI -->|Response| Module1
    Module1 -->|Display Result| User

    User -->|Conversation| Module2[Module 2\nConversation Client]
    Module2 -->|Store History| History[(Conversation History)]
    Module2 -->|API Request with History| GroqAPI
    GroqAPI -->|Response| Module2
    Module2 -->|Display Result| User

    Client([Client App]) -->|HTTP Request| Module3[Module 3\nFlask API]
    Module3 -->|Store Session| Sessions[(Session Store)]
    Module3 -->|API Request| GroqAPI
    GroqAPI -->|Response| Module3
    Module3 -->|HTTP Response| Client
```
