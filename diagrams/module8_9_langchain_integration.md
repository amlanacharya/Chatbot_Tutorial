# Module 8-9: LangChain Integration

This document contains diagrams illustrating the LangChain integration in modules 8 and 9.

## LangChain Architecture (Module 8)

```mermaid
graph TD
    subgraph "Flask API Server"
        API[Flask App]
        Routes[API Routes]
    end
    
    subgraph "LangChain Components"
        GroqLLM[Custom GroqLLM]
        ConversationChain[Conversation Chain]
        Memory[Conversation Memory]
        Prompt[Chat Prompt Template]
    end
    
    subgraph "Storage"
        ConversationChains[(Conversation Chains)]
    end
    
    subgraph "External"
        Client[Client Applications]
        GroqAPI[Groq API]
    end
    
    %% Connections
    Client -->|HTTP Requests| API
    API -->|Route Handling| Routes
    
    Routes -->|Create/Get Chain| ConversationChains
    ConversationChains -->|Retrieve| ConversationChain
    
    ConversationChain -->|Use| GroqLLM
    ConversationChain -->|Use| Memory
    ConversationChain -->|Use| Prompt
    
    GroqLLM -->|API Call| GroqAPI
    GroqAPI -->|Response| GroqLLM
    
    ConversationChain -->|Response| Routes
    Routes -->|HTTP Response| Client
    
    classDef api fill:#bbf,stroke:#333,stroke-width:2px;
    classDef langchain fill:#f9f,stroke:#333,stroke-width:2px;
    classDef storage fill:#fdb,stroke:#333,stroke-width:2px;
    classDef external fill:#fbb,stroke:#333,stroke-width:2px;
    
    class API,Routes api;
    class GroqLLM,ConversationChain,Memory,Prompt langchain;
    class ConversationChains storage;
    class Client,GroqAPI external;
```

## LangChain Class Diagram

```mermaid
classDiagram
    class GroqLLM {
        +model_name: str
        +temperature: float
        +max_tokens: int
        +top_p: float
        +groq_api_key: str
        +__init__(groq_api_key, model_name, temperature, max_tokens, top_p)
        +_call(prompt, stop): str
        +_llm_type(): str
        +_identifying_params(): Mapping
    }
    
    class ConversationChain {
        +llm: LLM
        +memory: Memory
        +verbose: bool
        +predict(input): str
    }
    
    class ConversationBufferMemory {
        +buffer: str
        +clear()
        +save_context(inputs, outputs)
        +load_memory_variables(inputs): dict
    }
    
    class LLM {
        <<abstract>>
        +_call(prompt, stop): str
        +_llm_type(): str
    }
    
    LLM <|-- GroqLLM
    ConversationChain o-- LLM
    ConversationChain o-- ConversationBufferMemory
```

## LangChain Sequence Diagram

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask API
    participant ChainMgr as Chain Manager
    participant Chain as Conversation Chain
    participant Memory as Buffer Memory
    participant LLM as GroqLLM
    participant GroqAPI as Groq API

    Client->>API: Send message with session ID
    API->>ChainMgr: Get conversation chain
    
    alt New Session
        ChainMgr->>LLM: Create new LLM instance
        ChainMgr->>Memory: Create new memory
        ChainMgr->>Chain: Create new chain with LLM and memory
        ChainMgr->>ChainMgr: Store chain for session
    else Existing Session
        ChainMgr->>ChainMgr: Retrieve existing chain
    end
    
    API->>Chain: Process message
    Chain->>Memory: Load conversation context
    Memory-->>Chain: Return context
    Chain->>LLM: Generate response with context
    LLM->>GroqAPI: Send API request
    GroqAPI-->>LLM: Return response
    LLM-->>Chain: Return generated text
    Chain->>Memory: Save new context
    Chain-->>API: Return response
    API-->>Client: Return response
```

## Agent Framework (Module 9)

```mermaid
graph TD
    subgraph "Agent Components"
        Agent[LangChain Agent]
        Tools[Tool Registry]
        Executor[Agent Executor]
        OutputParser[Output Parser]
    end
    
    subgraph "Available Tools"
        WebSearch[Web Search Tool]
        Calculator[Calculator Tool]
        Weather[Weather Tool]
    end
    
    subgraph "LangChain Components"
        LLM[GroqLLM]
        Memory[Conversation Memory]
        Prompt[Agent Prompt Template]
    end
    
    subgraph "External"
        GroqAPI[Groq API]
        WebAPI[Web Search API]
        WeatherAPI[Weather API]
    end
    
    %% Connections
    Agent -->|Uses| LLM
    Agent -->|Uses| Tools
    Agent -->|Uses| Prompt
    Agent -->|Uses| OutputParser
    
    Executor -->|Runs| Agent
    Executor -->|Manages| Memory
    
    Tools -->|Registers| WebSearch
    Tools -->|Registers| Calculator
    Tools -->|Registers| Weather
    
    WebSearch -->|Calls| WebAPI
    Weather -->|Calls| WeatherAPI
    
    LLM -->|Calls| GroqAPI
    
    classDef agent fill:#f9f,stroke:#333,stroke-width:2px;
    classDef tools fill:#bfb,stroke:#333,stroke-width:2px;
    classDef langchain fill:#bbf,stroke:#333,stroke-width:2px;
    classDef external fill:#fbb,stroke:#333,stroke-width:2px;
    
    class Agent,Tools,Executor,OutputParser agent;
    class WebSearch,Calculator,Weather tools;
    class LLM,Memory,Prompt langchain;
    class GroqAPI,WebAPI,WeatherAPI external;
```

## Agent Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent as LangChain Agent
    participant LLM as GroqLLM
    participant Tools as Tool Registry
    participant Tool as Specific Tool
    participant API as External API

    User->>Agent: Submit query
    Agent->>LLM: Generate action plan
    LLM-->>Agent: Return action and tool
    
    loop Tool Execution
        Agent->>Tools: Request tool
        Tools->>Tool: Execute tool function
        
        alt External API needed
            Tool->>API: Make API call
            API-->>Tool: Return data
        end
        
        Tool-->>Tools: Return result
        Tools-->>Agent: Return tool output
        
        Agent->>LLM: Process tool output
        LLM-->>Agent: Decide next action
    end
    
    Agent->>LLM: Generate final response
    LLM-->>Agent: Return formatted response
    Agent-->>User: Return complete answer
```

## Agent State Diagram

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Ready: Load Tools
    
    Ready --> Planning: Receive Query
    Planning --> ToolSelection: Generate Plan
    
    ToolSelection --> ToolExecution: Select Tool
    ToolExecution --> ResultEvaluation: Execute Tool
    
    ResultEvaluation --> ToolSelection: Need More Info
    ResultEvaluation --> ResponseGeneration: Have Answer
    
    ResponseGeneration --> Ready: Return Response
    
    Ready --> [*]: Shutdown
```
