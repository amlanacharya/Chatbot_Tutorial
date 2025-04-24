# Module 14: Agent Framework

This document contains diagrams illustrating the agent framework architecture and components in module 14.

## Agent Framework Architecture

```mermaid
graph TD
    subgraph "Agent Core"
        AgentFramework[Agent Framework]
        TaskPlanner[Task Planner]
        ToolExecutor[Tool Executor]
        StateManager[State Manager]
        DecisionMaker[Decision Maker]
    end
    
    subgraph "Tool Registry"
        ToolRegistry[Tool Registry]
        
        subgraph "Available Tools"
            Calculator[Calculator Tool]
            CurrentTime[Current Time Tool]
            Wikipedia[Wikipedia Search Tool]
            Weather[Weather Tool]
            WebSearch[Web Search Tool]
        end
    end
    
    subgraph "LLM Integration"
        LLMClient[LLM Client]
        PromptTemplates[Prompt Templates]
        ResponseParser[Response Parser]
    end
    
    subgraph "External"
        GroqAPI[Groq API]
        ExternalServices[External Services]
    end
    
    %% Connections
    AgentFramework -->|Plans Tasks| TaskPlanner
    AgentFramework -->|Executes Tools| ToolExecutor
    AgentFramework -->|Manages State| StateManager
    AgentFramework -->|Makes Decisions| DecisionMaker
    
    ToolExecutor -->|Uses| ToolRegistry
    ToolRegistry -->|Registers| Calculator
    ToolRegistry -->|Registers| CurrentTime
    ToolRegistry -->|Registers| Wikipedia
    ToolRegistry -->|Registers| Weather
    ToolRegistry -->|Registers| WebSearch
    
    TaskPlanner -->|Uses| LLMClient
    DecisionMaker -->|Uses| LLMClient
    
    LLMClient -->|Uses| PromptTemplates
    LLMClient -->|Uses| ResponseParser
    LLMClient -->|Calls| GroqAPI
    
    Calculator -->|Self-contained| Calculator
    CurrentTime -->|Self-contained| CurrentTime
    Wikipedia -->|Calls| ExternalServices
    Weather -->|Calls| ExternalServices
    WebSearch -->|Calls| ExternalServices
    
    classDef core fill:#f9f,stroke:#333,stroke-width:2px;
    classDef tools fill:#bbf,stroke:#333,stroke-width:2px;
    classDef llm fill:#bfb,stroke:#333,stroke-width:2px;
    classDef external fill:#fbb,stroke:#333,stroke-width:2px;
    
    class AgentFramework,TaskPlanner,ToolExecutor,StateManager,DecisionMaker core;
    class ToolRegistry,Calculator,CurrentTime,Wikipedia,Weather,WebSearch tools;
    class LLMClient,PromptTemplates,ResponseParser llm;
    class GroqAPI,ExternalServices external;
```

## Agent Framework Class Diagram

```mermaid
classDiagram
    class AgentFramework {
        -llm_client: LLMClient
        -tool_registry: ToolRegistry
        -state_manager: StateManager
        +__init__(api_key, model)
        +process_input(user_input): dict
        +execute_task(task): dict
        +get_state(): dict
    }
    
    class ToolRegistry {
        -tools: dict
        +__init__()
        +register_tool(name, description, function, parameters)
        +get_tool(name): dict
        +list_tools(): list
        +execute_tool(name, **kwargs): any
    }
    
    class LLMClient {
        -api_key: str
        -model: str
        -base_url: str
        +__init__(api_key, model)
        +generate_response(messages): str
        +parse_structured_output(response, schema): dict
    }
    
    class StateManager {
        -conversation_history: list
        -task_history: list
        -current_task: dict
        +__init__()
        +add_message(role, content)
        +add_task(task)
        +update_task_status(task_id, status)
        +get_conversation_history(): list
        +get_task_history(): list
    }
    
    class TaskPlanner {
        -llm_client: LLMClient
        +__init__(llm_client)
        +plan_task(user_input): list
        +break_down_task(task): list
    }
    
    class ToolExecutor {
        -tool_registry: ToolRegistry
        +__init__(tool_registry)
        +execute_tool(tool_name, **params): any
        +execute_step(step): dict
    }
    
    class Tool {
        <<interface>>
        +name: str
        +description: str
        +parameters: dict
        +execute(**kwargs): any
    }
    
    class CalculatorTool {
        +name: str
        +description: str
        +parameters: dict
        +execute(expression): float
    }
    
    class WikipediaTool {
        +name: str
        +description: str
        +parameters: dict
        +execute(query): str
    }
    
    AgentFramework o-- LLMClient
    AgentFramework o-- ToolRegistry
    AgentFramework o-- StateManager
    AgentFramework o-- TaskPlanner
    AgentFramework o-- ToolExecutor
    
    TaskPlanner o-- LLMClient
    ToolExecutor o-- ToolRegistry
    
    ToolRegistry o-- Tool
    
    Tool <|-- CalculatorTool
    Tool <|-- WikipediaTool
```

## Agent Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent Framework
    participant Planner as Task Planner
    participant LLM as LLM Client
    participant Executor as Tool Executor
    participant Tools as Tool Registry
    participant State as State Manager

    User->>Agent: Submit input
    Agent->>State: Add user message
    Agent->>Planner: Plan task
    
    Planner->>LLM: Generate task plan
    LLM-->>Planner: Return structured plan
    Planner-->>Agent: Return task steps
    
    Agent->>State: Store task plan
    
    loop For each step
        Agent->>Executor: Execute step
        
        alt Step requires tool
            Executor->>Tools: Get tool
            Tools-->>Executor: Return tool
            Executor->>Tools: Execute tool with params
            Tools-->>Executor: Return tool result
        else No tool required
            Executor->>LLM: Generate response for step
            LLM-->>Executor: Return response
        end
        
        Executor-->>Agent: Return step result
        Agent->>State: Update task status
    end
    
    Agent->>LLM: Generate final response
    LLM-->>Agent: Return formatted response
    
    Agent->>State: Add assistant message
    Agent-->>User: Return response
```

## Tool Execution Flow

```mermaid
flowchart TD
    Start([Start]) --> ParseInput[Parse User Input]
    ParseInput --> PlanTask[Plan Task]
    PlanTask --> HasTools{Requires\nTools?}
    
    HasTools -->|Yes| IdentifyTool[Identify Required Tool]
    HasTools -->|No| GenerateResponse[Generate Direct Response]
    
    IdentifyTool --> ToolExists{Tool\nExists?}
    
    ToolExists -->|No| HandleMissingTool[Handle Missing Tool]
    HandleMissingTool --> GenerateResponse
    
    ToolExists -->|Yes| ExtractParams[Extract Tool Parameters]
    ExtractParams --> ValidParams{Valid\nParameters?}
    
    ValidParams -->|No| RequestMoreInfo[Request More Information]
    RequestMoreInfo --> End
    
    ValidParams -->|Yes| ExecuteTool[Execute Tool]
    ExecuteTool --> ProcessResult[Process Tool Result]
    ProcessResult --> NeedMoreTools{Need More\nTools?}
    
    NeedMoreTools -->|Yes| IdentifyTool
    NeedMoreTools -->|No| GenerateResponse
    
    GenerateResponse --> End([End])
```

## Agent State Diagram

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Ready: Load Tools
    
    Ready --> Planning: Receive Input
    Planning --> ToolSelection: Generate Plan
    
    ToolSelection --> ToolExecution: Select Tool
    ToolExecution --> ResultEvaluation: Execute Tool
    
    ResultEvaluation --> ToolSelection: Need More Tools
    ResultEvaluation --> ResponseGeneration: Complete Task
    
    ResponseGeneration --> Ready: Return Response
    
    Ready --> [*]: Shutdown
```

## Multi-Agent System Architecture

```mermaid
graph TD
    subgraph "Multi-Agent System"
        Coordinator[Coordinator Agent]
        
        subgraph "Specialized Agents"
            Planner[Planner Agent]
            Researcher[Research Agent]
            Executor[Execution Agent]
            Critic[Critic Agent]
        end
    end
    
    subgraph "Shared Resources"
        TaskQueue[Task Queue]
        KnowledgeBase[Knowledge Base]
        ToolRegistry[Tool Registry]
    end
    
    subgraph "External"
        User[User]
        LLMProvider[LLM Provider]
        ExternalServices[External Services]
    end
    
    %% Connections
    User -->|Request| Coordinator
    
    Coordinator -->|Delegate Planning| Planner
    Coordinator -->|Delegate Research| Researcher
    Coordinator -->|Delegate Execution| Executor
    Coordinator -->|Delegate Evaluation| Critic
    
    Planner -->|Create Tasks| TaskQueue
    Researcher -->|Read Tasks| TaskQueue
    Researcher -->|Store Information| KnowledgeBase
    Executor -->|Read Tasks| TaskQueue
    Executor -->|Read Information| KnowledgeBase
    Executor -->|Use Tools| ToolRegistry
    Critic -->|Read Results| KnowledgeBase
    
    Planner -->|Use| LLMProvider
    Researcher -->|Use| LLMProvider
    Executor -->|Use| LLMProvider
    Critic -->|Use| LLMProvider
    
    Researcher -->|Query| ExternalServices
    Executor -->|Call| ExternalServices
    
    Coordinator -->|Response| User
    
    classDef coordinator fill:#f9f,stroke:#333,stroke-width:2px;
    classDef agents fill:#bbf,stroke:#333,stroke-width:2px;
    classDef resources fill:#bfb,stroke:#333,stroke-width:2px;
    classDef external fill:#fbb,stroke:#333,stroke-width:2px;
    
    class Coordinator coordinator;
    class Planner,Researcher,Executor,Critic agents;
    class TaskQueue,KnowledgeBase,ToolRegistry resources;
    class User,LLMProvider,ExternalServices external;
```
