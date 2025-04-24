# Module 4-5: UI Integration Diagrams

This document contains diagrams illustrating the UI integration in modules 4 and 5 (Gradio and Streamlit interfaces).

## Sequence Diagram for Gradio UI (Module 4)

```mermaid
sequenceDiagram
    participant User
    participant GradioUI as Gradio UI (Module 4)
    participant FlaskAPI as Flask API (Module 3)
    participant GroqAPI as Groq API

    User->>GradioUI: Access UI
    GradioUI->>FlaskAPI: Fetch available models
    FlaskAPI-->>GradioUI: Return models list
    GradioUI->>GradioUI: Initialize session ID
    GradioUI->>GradioUI: Display chat interface
    
    loop Chat Interaction
        User->>GradioUI: Enter message
        GradioUI->>FlaskAPI: Send chat request with message, session ID, model
        FlaskAPI->>GroqAPI: Forward request to Groq
        GroqAPI-->>FlaskAPI: Return response
        FlaskAPI-->>GradioUI: Return formatted response
        GradioUI->>GradioUI: Update chat history
        GradioUI-->>User: Display response
    end
    
    alt Clear Conversation
        User->>GradioUI: Click "Clear Conversation"
        GradioUI->>FlaskAPI: Send clear request with session ID
        FlaskAPI-->>GradioUI: Confirm cleared
        GradioUI->>GradioUI: Reset chat display
        GradioUI-->>User: Show empty chat
    end
    
    alt Change Model
        User->>GradioUI: Select different model
        GradioUI->>GradioUI: Update model selection
        Note over GradioUI: Next message will use new model
    end
```

## Sequence Diagram for Streamlit UI (Module 5)

```mermaid
sequenceDiagram
    participant User
    participant StreamlitUI as Streamlit UI (Module 5)
    participant FlaskAPI as Flask API (Module 3)
    participant GroqAPI as Groq API

    User->>StreamlitUI: Access UI
    StreamlitUI->>StreamlitUI: Initialize session state
    StreamlitUI->>FlaskAPI: Fetch available models
    FlaskAPI-->>StreamlitUI: Return models list
    StreamlitUI->>StreamlitUI: Display UI with sidebar
    
    loop Chat Interaction
        User->>StreamlitUI: Enter message
        StreamlitUI->>StreamlitUI: Add message to session state
        StreamlitUI->>FlaskAPI: Send chat request with message, session ID, model
        FlaskAPI->>GroqAPI: Forward request to Groq
        GroqAPI-->>FlaskAPI: Return response
        FlaskAPI-->>StreamlitUI: Return formatted response
        StreamlitUI->>StreamlitUI: Add response to session state
        StreamlitUI-->>User: Display response
    end
    
    alt Clear Conversation
        User->>StreamlitUI: Click "Clear Conversation"
        StreamlitUI->>FlaskAPI: Send clear request with session ID
        FlaskAPI-->>StreamlitUI: Confirm cleared
        StreamlitUI->>StreamlitUI: Reset session state messages
        StreamlitUI-->>User: Show empty chat
    end
    
    alt Change Model
        User->>StreamlitUI: Select different model in sidebar
        StreamlitUI->>StreamlitUI: Update model in session state
        StreamlitUI->>FlaskAPI: Send model change request
        FlaskAPI-->>StreamlitUI: Confirm model changed
        Note over StreamlitUI: Next message will use new model
    end
```

## Component Diagram for UI Integration

```mermaid
graph TD
    subgraph "User Interfaces"
        GradioUI[Gradio UI\nModule 4]
        StreamlitUI[Streamlit UI\nModule 5]
    end
    
    subgraph "Backend API"
        FlaskAPI[Flask API\nModule 3]
        SessionStore[(Session Store)]
        ModelRegistry[(Model Registry)]
    end
    
    subgraph "External Services"
        GroqAPI[Groq API]
    end
    
    %% Connections
    GradioUI -->|API Requests| FlaskAPI
    StreamlitUI -->|API Requests| FlaskAPI
    
    FlaskAPI -->|Store/Retrieve| SessionStore
    FlaskAPI -->|Get Models| ModelRegistry
    FlaskAPI -->|LLM Requests| GroqAPI
    
    GroqAPI -->|Responses| FlaskAPI
    FlaskAPI -->|API Responses| GradioUI
    FlaskAPI -->|API Responses| StreamlitUI
    
    classDef ui fill:#f9f,stroke:#333,stroke-width:2px;
    classDef api fill:#bbf,stroke:#333,stroke-width:2px;
    classDef external fill:#fbb,stroke:#333,stroke-width:2px;
    
    class GradioUI,StreamlitUI ui;
    class FlaskAPI,SessionStore,ModelRegistry api;
    class GroqAPI external;
```

## State Diagram for UI Session

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> Ready: Load UI
    
    Ready --> Processing: Send Message
    Processing --> Ready: Display Response
    
    Ready --> Clearing: Clear Conversation
    Clearing --> Ready: Reset Display
    
    Ready --> ChangingModel: Select New Model
    ChangingModel --> Ready: Update Model
    
    Ready --> [*]: Close Browser
```
