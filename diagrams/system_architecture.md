# System Architecture Diagram

This diagram shows the overall architecture of the chatbot system and how the different modules interact.

```mermaid
graph TD
    subgraph "Client Layer"
        CLI[Command Line Interface]
        GradioUI[Gradio UI - Module 4]
        StreamlitUI[Streamlit UI - Module 5]
        AdvancedUI[Advanced UI - Module 7]
    end

    subgraph "API Layer"
        API[Flask API - Module 3]
        LangChainAPI[LangChain API - Module 8]
        AgentAPI[Agent API - Module 14]
    end

    subgraph "Core Layer"
        BasicClient[Basic Client - Module 1]
        ConversationClient[Conversation Client - Module 2]
        MemoryManager[Memory Manager - Module 6]
        ModelOptimizer[Model Optimizer - Module 10-11]
        AsyncProcessor[Async Processor - Module 12]
    end

    subgraph "External Services"
        GroqAPI[Groq API]
        OtherLLMs[Other LLM Providers]
    end

    subgraph "Deployment"
        Docker[Docker Container - Module 13]
        CloudDeploy[Cloud Deployment - Module 13]
    end

    %% Connections
    CLI --> BasicClient
    CLI --> ConversationClient
    
    GradioUI --> API
    StreamlitUI --> API
    AdvancedUI --> API
    
    API --> BasicClient
    API --> ConversationClient
    API --> MemoryManager
    
    LangChainAPI --> ConversationClient
    LangChainAPI --> MemoryManager
    
    AgentAPI --> LangChainAPI
    
    BasicClient --> GroqAPI
    ConversationClient --> GroqAPI
    LangChainAPI --> GroqAPI
    LangChainAPI --> OtherLLMs
    
    API --> Docker
    LangChainAPI --> Docker
    AgentAPI --> Docker
    
    Docker --> CloudDeploy
    
    ModelOptimizer --> BasicClient
    ModelOptimizer --> ConversationClient
    
    AsyncProcessor --> API
    AsyncProcessor --> LangChainAPI
    
    classDef module fill:#f9f,stroke:#333,stroke-width:2px;
    class GradioUI,StreamlitUI,AdvancedUI,API,LangChainAPI,AgentAPI,BasicClient,ConversationClient,MemoryManager,ModelOptimizer,AsyncProcessor,Docker,CloudDeploy module;
```

## Component Descriptions

### Client Layer
- **Command Line Interface**: Direct interaction with the core clients
- **Gradio UI (Module 4)**: Simple web UI for chatbot interaction
- **Streamlit UI (Module 5)**: More advanced web UI with additional features
- **Advanced UI (Module 7)**: UI for model comparison and performance metrics

### API Layer
- **Flask API (Module 3)**: RESTful API for chatbot interactions
- **LangChain API (Module 8)**: API with LangChain integration for advanced features
- **Agent API (Module 14)**: API for agent-based interactions with tools

### Core Layer
- **Basic Client (Module 1)**: Simple client for Groq API interaction
- **Conversation Client (Module 2)**: Client with conversation history management
- **Memory Manager (Module 6)**: Advanced memory management for conversations
- **Model Optimizer (Module 10-11)**: Optimization for model deployment and performance
- **Async Processor (Module 12)**: Asynchronous processing for improved performance

### External Services
- **Groq API**: Primary LLM provider
- **Other LLM Providers**: Alternative LLM services

### Deployment
- **Docker Container (Module 13)**: Containerization for deployment
- **Cloud Deployment (Module 13)**: Cloud deployment options
