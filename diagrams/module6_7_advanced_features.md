# Module 6-7: Advanced Features and Model Comparison

This document contains diagrams illustrating the advanced features in modules 6 and 7, focusing on memory management and model comparison.

## Memory Management Architecture (Module 6)

```mermaid
graph TD
    subgraph "Memory Management System"
        MemoryManager[Memory Manager]
        TokenCounter[Token Counter]
        
        subgraph "Memory Types"
            WindowMemory[Window Memory]
            SummaryMemory[Summary Memory]
            TokenWindowMemory[Token Window Memory]
        end
    end
    
    subgraph "API Integration"
        API[Flask API]
        Conversations[(Conversation Store)]
    end
    
    subgraph "External"
        GroqAPI[Groq API]
        Client[Client Applications]
    end
    
    %% Connections
    Client -->|Requests| API
    API -->|Manage Memory| MemoryManager
    
    MemoryManager -->|Count Tokens| TokenCounter
    MemoryManager -->|Use| WindowMemory
    MemoryManager -->|Use| SummaryMemory
    MemoryManager -->|Use| TokenWindowMemory
    
    MemoryManager -->|Store| Conversations
    API -->|Retrieve| Conversations
    
    API -->|Send Requests| GroqAPI
    GroqAPI -->|Responses| API
    API -->|Responses| Client
    
    classDef memory fill:#f9f,stroke:#333,stroke-width:2px;
    classDef api fill:#bbf,stroke:#333,stroke-width:2px;
    classDef external fill:#fbb,stroke:#333,stroke-width:2px;
    
    class MemoryManager,TokenCounter,WindowMemory,SummaryMemory,TokenWindowMemory memory;
    class API,Conversations api;
    class GroqAPI,Client external;
```

## Memory Management Sequence Diagram

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask API
    participant MemoryMgr as Memory Manager
    participant TokenCounter
    participant Memory as Memory Implementation
    participant GroqAPI as Groq API

    Client->>API: Send message with session ID
    API->>MemoryMgr: Get memory for session
    
    alt New Session
        MemoryMgr->>MemoryMgr: Create new memory instance
    else Existing Session
        MemoryMgr->>Memory: Retrieve existing memory
    end
    
    API->>MemoryMgr: Add user message
    MemoryMgr->>TokenCounter: Count message tokens
    TokenCounter-->>MemoryMgr: Return token count
    
    alt Token Limit Exceeded
        MemoryMgr->>Memory: Trim or summarize history
    end
    
    MemoryMgr->>Memory: Store updated history
    API->>GroqAPI: Send request with managed history
    GroqAPI-->>API: Return response
    
    API->>MemoryMgr: Add assistant response
    MemoryMgr->>TokenCounter: Count response tokens
    TokenCounter-->>MemoryMgr: Return token count
    MemoryMgr->>Memory: Store updated history
    
    API-->>Client: Return response
```

## Model Comparison Flow (Module 7)

```mermaid
graph TD
    subgraph "Model Comparison UI"
        ComparisonTab[Comparison Tab]
        PromptInput[Prompt Input]
        ModelSelection[Model Selection]
        SystemMsgInput[System Message Input]
        ParamControls[Parameter Controls]
        CompareButton[Compare Button]
        ResultsDisplay[Results Display]
        Charts[Visualization Charts]
    end
    
    subgraph "API Layer"
        CompareAPI[Compare Models API]
        ModelRegistry[Model Registry]
    end
    
    subgraph "Processing"
        ParallelExecution[Parallel Execution]
        ResponseCollection[Response Collection]
        MetricsCalculation[Metrics Calculation]
    end
    
    subgraph "External"
        GroqAPI[Groq API]
    end
    
    %% Flow
    PromptInput -->|Input Text| CompareButton
    ModelSelection -->|Selected Models| CompareButton
    SystemMsgInput -->|System Message| CompareButton
    ParamControls -->|Parameters| CompareButton
    
    CompareButton -->|Request| CompareAPI
    CompareAPI -->|Get Models| ModelRegistry
    CompareAPI -->|Execute| ParallelExecution
    
    ParallelExecution -->|Model 1 Request| GroqAPI
    ParallelExecution -->|Model 2 Request| GroqAPI
    ParallelExecution -->|Model N Request| GroqAPI
    
    GroqAPI -->|Model 1 Response| ResponseCollection
    GroqAPI -->|Model 2 Response| ResponseCollection
    GroqAPI -->|Model N Response| ResponseCollection
    
    ResponseCollection -->|All Responses| MetricsCalculation
    MetricsCalculation -->|Results| CompareAPI
    CompareAPI -->|Comparison Data| ResultsDisplay
    ResultsDisplay -->|Data| Charts
    
    classDef ui fill:#f9f,stroke:#333,stroke-width:2px;
    classDef api fill:#bbf,stroke:#333,stroke-width:2px;
    classDef process fill:#bfb,stroke:#333,stroke-width:2px;
    classDef external fill:#fbb,stroke:#333,stroke-width:2px;
    
    class ComparisonTab,PromptInput,ModelSelection,SystemMsgInput,ParamControls,CompareButton,ResultsDisplay,Charts ui;
    class CompareAPI,ModelRegistry api;
    class ParallelExecution,ResponseCollection,MetricsCalculation process;
    class GroqAPI external;
```

## Performance Metrics Dashboard Flow

```mermaid
graph TD
    subgraph "Performance Metrics UI"
        MetricsTab[Metrics Tab]
        RefreshButton[Refresh Button]
        TimeChart[Response Time Chart]
        UsageChart[Usage Distribution Chart]
        TokenTable[Token Usage Table]
    end
    
    subgraph "API Layer"
        PerformanceAPI[Performance API]
        StatsCollector[Statistics Collector]
    end
    
    subgraph "Data Storage"
        UsageStats[(Usage Statistics)]
        ResponseTimes[(Response Times)]
        TokenCounts[(Token Counts)]
    end
    
    %% Flow
    RefreshButton -->|Request| PerformanceAPI
    PerformanceAPI -->|Collect| StatsCollector
    
    StatsCollector -->|Read| UsageStats
    StatsCollector -->|Read| ResponseTimes
    StatsCollector -->|Read| TokenCounts
    
    StatsCollector -->|Aggregated Data| PerformanceAPI
    PerformanceAPI -->|Response Time Data| TimeChart
    PerformanceAPI -->|Usage Data| UsageChart
    PerformanceAPI -->|Token Data| TokenTable
    
    classDef ui fill:#f9f,stroke:#333,stroke-width:2px;
    classDef api fill:#bbf,stroke:#333,stroke-width:2px;
    classDef storage fill:#fdb,stroke:#333,stroke-width:2px;
    
    class MetricsTab,RefreshButton,TimeChart,UsageChart,TokenTable ui;
    class PerformanceAPI,StatsCollector api;
    class UsageStats,ResponseTimes,TokenCounts storage;
```

## State Diagram for Model Comparison

```mermaid
stateDiagram-v2
    [*] --> Ready
    
    Ready --> ConfiguringComparison: Open Comparison Tab
    
    ConfiguringComparison --> EnteringPrompt: Enter Prompt
    EnteringPrompt --> SelectingModels: Select Models
    SelectingModels --> ConfiguringParams: Configure Parameters
    ConfiguringParams --> ReadyToCompare: Review Settings
    
    ReadyToCompare --> Comparing: Click Compare
    Comparing --> DisplayingResults: Receive Results
    DisplayingResults --> AnalyzingCharts: View Charts
    
    AnalyzingCharts --> ConfiguringComparison: Modify Settings
    
    DisplayingResults --> Ready: Close Comparison
    AnalyzingCharts --> Ready: Close Comparison
```
