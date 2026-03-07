# AI Retail Intelligence - AWS Architecture Diagram

## Complete System Architecture

```mermaid
graph TB
    subgraph "User Layer"
        USER[👤 End Users<br/>Web Browsers]
    end

    subgraph "AWS Cloud - Region: us-east-1"
        subgraph "Frontend - Static Hosting"
            S3[📦 Amazon S3<br/>ai-retail-dashboard<br/>Static Website Hosting]
        end

        subgraph "API Layer"
            APIGW[🌐 API Gateway<br/>foiwdbvnx6<br/>REST API]
        end

        subgraph "Compute Layer - Lambda Functions"
            L1[⚡ Lambda<br/>ai-retail-forecast<br/>Price Forecasting<br/>6 AI Models]
            L2[⚡ Lambda<br/>ai-retail-current-prices<br/>Current Price Data]
            L3[⚡ Lambda<br/>ai-retail-market-copilot<br/>AI Q&A Assistant]
            L4[⚡ Lambda<br/>ai-retail-document-analysis<br/>Document Analysis<br/>7 AI Models]
            L5[⚡ Lambda<br/>ai-retail-forecast-hybrid<br/>Hybrid Forecasting<br/>Forecast + Bedrock]
            L6[⚡ Lambda<br/>ai-retail-document-history<br/>History Retrieval]
        end

        subgraph "AI/ML Services"
            BEDROCK_EAST[🤖 Amazon Bedrock<br/>us-east-1<br/>Nova Models<br/>• Nova Micro<br/>• Nova Lite<br/>• Nova Pro]
            BEDROCK_WEST[🤖 Amazon Bedrock<br/>us-west-2<br/>Llama Models<br/>• Llama 3.2 3B<br/>• Llama 3.1 8B<br/>• Llama 3.3 70B<br/>• Llama 4 Scout]
            FORECAST[📊 Amazon Forecast<br/>Time Series ML<br/>Optional]
        end

        subgraph "Data Storage"
            DYNAMO1[🗄️ DynamoDB<br/>CurrentPrices<br/>Gold/Silver/ETF Data]
            DYNAMO2[🗄️ DynamoDB<br/>DocumentAnalysisHistory<br/>90-day TTL]
        end

        subgraph "Security & Access"
            IAM[🔐 IAM Role<br/>AIRetailIntelligenceLambdaRole<br/>Bedrock + DynamoDB Permissions]
        end
    end

    %% User to Frontend
    USER -->|HTTPS| S3

    %% Frontend to API Gateway
    S3 -->|API Calls| APIGW

    %% API Gateway to Lambda Functions
    APIGW -->|POST /forecast| L1
    APIGW -->|GET /current-prices| L2
    APIGW -->|POST /market-copilot| L3
    APIGW -->|POST /analyze-document| L4
    APIGW -->|POST /forecast-hybrid| L5
    APIGW -->|GET /document-history| L6

    %% Lambda to Bedrock
    L1 -.->|Invoke Models| BEDROCK_EAST
    L3 -.->|Invoke Models| BEDROCK_EAST
    L4 -.->|Invoke Nova| BEDROCK_EAST
    L4 -.->|Invoke Llama| BEDROCK_WEST
    L5 -.->|Invoke Models| BEDROCK_EAST

    %% Lambda to Forecast
    L5 -.->|Optional| FORECAST

    %% Lambda to DynamoDB
    L2 -->|Read/Write| DYNAMO1
    L4 -->|Write History| DYNAMO2
    L6 -->|Read History| DYNAMO2

    %% IAM Permissions
    IAM -.->|Authorize| L1
    IAM -.->|Authorize| L2
    IAM -.->|Authorize| L3
    IAM -.->|Authorize| L4
    IAM -.->|Authorize| L5
    IAM -.->|Authorize| L6

    %% Styling
    classDef awsOrange fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsBlue fill:#3B48CC,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsGreen fill:#3F8624,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsPurple fill:#8B5CF6,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsRed fill:#DD344C,stroke:#232F3E,stroke-width:2px,color:#fff
    
    class S3 awsOrange
    class APIGW awsPurple
    class L1,L2,L3,L4,L5,L6 awsOrange
    class BEDROCK_EAST,BEDROCK_WEST,FORECAST awsGreen
    class DYNAMO1,DYNAMO2 awsBlue
    class IAM awsRed
```

## Data Flow Diagrams

### 1. Price Forecasting Flow

```mermaid
sequenceDiagram
    participant User
    participant S3 as S3 Dashboard
    participant API as API Gateway
    participant Lambda as Lambda Forecast
    participant Bedrock as Amazon Bedrock
    participant DynamoDB

    User->>S3: Access Dashboard
    S3->>User: Load Web Interface
    User->>API: POST /forecast (symbol, model)
    API->>Lambda: Invoke Function
    Lambda->>DynamoDB: Get Historical Prices
    DynamoDB-->>Lambda: Price Data
    Lambda->>Bedrock: Invoke AI Model
    Bedrock-->>Lambda: Predictions + Analysis
    Lambda-->>API: Forecast Results
    API-->>User: JSON Response
    S3->>User: Display Charts
```

### 2. Document Analysis with History Flow

```mermaid
sequenceDiagram
    participant User
    participant S3 as S3 Dashboard
    participant API as API Gateway
    participant Lambda1 as Lambda Analysis
    participant Bedrock as Amazon Bedrock
    participant DynamoDB as DynamoDB History
    participant Lambda2 as Lambda History

    User->>S3: Access Document Analysis
    User->>API: POST /analyze-document
    API->>Lambda1: Invoke Function
    Lambda1->>Bedrock: Analyze Document
    Bedrock-->>Lambda1: Analysis Results
    Lambda1->>DynamoDB: Save to History
    Lambda1-->>API: Analysis + document_id
    API-->>User: Display Results
    
    Note over User,Lambda2: Later - View History
    User->>API: GET /document-history
    API->>Lambda2: Invoke Function
    Lambda2->>DynamoDB: Query History
    DynamoDB-->>Lambda2: Document List
    Lambda2-->>API: History Data
    API-->>User: Display History
```

### 3. Hybrid Forecasting Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway
    participant Lambda as Lambda Hybrid
    participant Forecast as Amazon Forecast
    participant Bedrock as Amazon Bedrock
    participant DynamoDB

    User->>API: POST /forecast-hybrid
    API->>Lambda: Invoke Function
    Lambda->>DynamoDB: Get Historical Data
    
    par Parallel Processing
        Lambda->>Forecast: Get ML Forecast
        Forecast-->>Lambda: Predictions
    and
        Lambda->>Bedrock: Get AI Analysis
        Bedrock-->>Lambda: Insights
    end
    
    Lambda->>Lambda: Combine Results
    Lambda-->>API: Hybrid Forecast
    API-->>User: Combined Response
```

## Component Details

### AWS Services Used

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Amazon S3** | Static website hosting for dashboard | Bucket: ai-retail-dashboard-439786465522<br/>Public read access<br/>Website hosting enabled |
| **API Gateway** | REST API endpoints | API ID: foiwdbvnx6<br/>Stage: prod<br/>CORS enabled |
| **AWS Lambda** | Serverless compute for business logic | 6 functions<br/>Python 3.11<br/>256-512 MB memory |
| **Amazon Bedrock** | AI/ML inference | 9 models across 2 regions<br/>Nova (us-east-1)<br/>Llama (us-west-2) |
| **DynamoDB** | NoSQL database | 2 tables<br/>Pay-per-request billing<br/>TTL enabled |
| **IAM** | Security and permissions | Role: AIRetailIntelligenceLambdaRole<br/>Bedrock + DynamoDB access |
| **Amazon Forecast** | Time series forecasting (optional) | Not yet configured |

### Lambda Functions

| Function | Runtime | Memory | Timeout | Purpose |
|----------|---------|--------|---------|---------|
| ai-retail-forecast | Python 3.11 | 512 MB | 60s | Price forecasting with 6 AI models |
| ai-retail-current-prices | Python 3.11 | 256 MB | 30s | Current price data retrieval |
| ai-retail-market-copilot | Python 3.11 | 512 MB | 60s | AI Q&A assistant |
| ai-retail-document-analysis | Python 3.11 | 512 MB | 60s | Document analysis with 7 AI models |
| ai-retail-forecast-hybrid | Python 3.11 | 512 MB | 60s | Hybrid forecasting (Forecast + Bedrock) |
| ai-retail-document-history | Python 3.11 | 256 MB | 30s | History retrieval from DynamoDB |

### AI Models Available

#### Document Analysis (7 Models)
- **Amazon Nova**: Micro, Lite, Pro
- **Meta Llama**: 3.2 3B, 3.1 8B, 3.3 70B, 4 Scout 17B

#### Price Forecasting (6 Models)
- **Amazon Nova**: Lite, Pro
- **Meta Llama**: 3.3 70B, 4 Scout 17B
- **DeepSeek**: V3, R1

### DynamoDB Tables

#### CurrentPrices
- **Partition Key**: symbol (String)
- **Attributes**: price, change, change_percent, timestamp
- **Purpose**: Store current gold, silver, ETF prices

#### DocumentAnalysisHistory
- **Partition Key**: document_id (String)
- **TTL**: 90 days
- **Attributes**: timestamp, text, analysis results, metadata
- **Purpose**: Store document analysis history

## Network Architecture

```mermaid
graph LR
    subgraph "Public Internet"
        USERS[👥 Users]
    end
    
    subgraph "AWS us-east-1"
        subgraph "Public Subnet"
            S3[S3 Website]
            APIGW[API Gateway]
        end
        
        subgraph "AWS Managed Services"
            LAMBDA[Lambda Functions]
            BEDROCK[Bedrock us-east-1]
            DYNAMO[DynamoDB]
        end
    end
    
    subgraph "AWS us-west-2"
        BEDROCK_W[Bedrock us-west-2<br/>Llama Models]
    end
    
    USERS -->|HTTPS| S3
    USERS -->|HTTPS| APIGW
    APIGW --> LAMBDA
    LAMBDA --> BEDROCK
    LAMBDA --> BEDROCK_W
    LAMBDA --> DYNAMO
    
    classDef public fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef private fill:#3B48CC,stroke:#232F3E,stroke-width:2px,color:#fff
    
    class S3,APIGW public
    class LAMBDA,BEDROCK,DYNAMO,BEDROCK_W private
```

## Cost Breakdown

### Monthly Cost Estimate (Moderate Usage)

| Service | Usage | Cost |
|---------|-------|------|
| **S3** | 1 GB storage + 10K requests | ~$0.50 |
| **API Gateway** | 100K requests | ~$0.35 |
| **Lambda** | 100K invocations, 512 MB | ~$2.00 |
| **Bedrock** | 1M tokens (mixed models) | ~$5.00 |
| **DynamoDB** | 1 GB storage, 100K requests | ~$1.50 |
| **Data Transfer** | 10 GB out | ~$0.90 |
| **Total** | | **~$10.25/month** |

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            HTTPS[HTTPS/TLS 1.2+]
            CORS[CORS Policies]
        end
        
        subgraph "Identity & Access"
            IAM[IAM Roles & Policies]
            RESOURCE[Resource-based Policies]
        end
        
        subgraph "Data Security"
            ENCRYPT[Encryption at Rest]
            TTL[TTL for Data Cleanup]
        end
        
        subgraph "API Security"
            THROTTLE[API Throttling]
            VALIDATE[Input Validation]
        end
    end
    
    HTTPS --> IAM
    CORS --> RESOURCE
    IAM --> ENCRYPT
    RESOURCE --> TTL
    ENCRYPT --> THROTTLE
    TTL --> VALIDATE
```

### Security Features

- ✅ HTTPS/TLS encryption for all traffic
- ✅ IAM role-based access control
- ✅ DynamoDB encryption at rest
- ✅ CORS policies for API access
- ✅ Input validation in Lambda functions
- ✅ API Gateway throttling
- ✅ 90-day TTL for automatic data cleanup
- ✅ No hardcoded credentials

## Deployment Architecture

```mermaid
graph LR
    subgraph "Development"
        CODE[Source Code<br/>GitHub]
    end
    
    subgraph "Deployment Scripts"
        SCRIPTS[Bash Scripts<br/>AWS CLI]
    end
    
    subgraph "AWS Resources"
        LAMBDA[Lambda Functions]
        S3[S3 Dashboard]
        DYNAMO[DynamoDB Tables]
        API[API Gateway]
    end
    
    CODE --> SCRIPTS
    SCRIPTS -->|Deploy| LAMBDA
    SCRIPTS -->|Upload| S3
    SCRIPTS -->|Create| DYNAMO
    SCRIPTS -->|Configure| API
    
    classDef dev fill:#3F8624,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef deploy fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    
    class CODE,SCRIPTS dev
    class LAMBDA,S3,DYNAMO,API deploy
```

## High Availability & Scalability

- **S3**: 99.99% availability, automatic scaling
- **API Gateway**: Automatic scaling, regional deployment
- **Lambda**: Auto-scaling, concurrent execution limits
- **DynamoDB**: Auto-scaling, on-demand capacity
- **Bedrock**: Managed service, automatic scaling

## Monitoring & Logging

```mermaid
graph TB
    subgraph "Monitoring Stack"
        CW[☁️ CloudWatch Logs]
        METRICS[📊 CloudWatch Metrics]
        ALARMS[🔔 CloudWatch Alarms]
    end
    
    subgraph "Log Sources"
        L1[Lambda Logs]
        L2[API Gateway Logs]
        L3[Application Logs]
    end
    
    L1 --> CW
    L2 --> CW
    L3 --> CW
    CW --> METRICS
    METRICS --> ALARMS
```

### Available Metrics

- Lambda invocations, duration, errors
- API Gateway requests, latency, 4xx/5xx errors
- DynamoDB read/write capacity, throttles
- Bedrock model invocations, token usage

## URLs & Endpoints

### Live URLs
- **Dashboard**: http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com
- **API Base**: https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod

### API Endpoints
- `POST /forecast` - Price forecasting
- `GET /current-prices` - Current prices
- `POST /market-copilot` - AI Q&A
- `POST /analyze-document` - Document analysis
- `POST /forecast-hybrid` - Hybrid forecasting
- `GET /document-history` - History retrieval

---

**Last Updated**: March 7, 2026  
**AWS Account**: 439786465522  
**Primary Region**: us-east-1  
**Secondary Region**: us-west-2 (Bedrock Llama models)
