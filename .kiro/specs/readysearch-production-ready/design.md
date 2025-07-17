# Design Document

## Overview

The ReadySearch Production-Ready Automation System is a comprehensive web application that combines a React-based frontend interface with a Python backend automation engine. The system enables users to search for names on ReadySearch.com.au through multiple input methods (manual entry, CSV import, JSON import) and provides real-time progress tracking with detailed result analysis.

Based on the research conducted on ReadySearch.com.au, the target search URL is `https://readysearch.com.au/products?person` which provides a person search interface with name input fields and optional birth year ranges.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web UI │◄──►│  Python Backend │◄──►│  ReadySearch    │
│   (Frontend)    │    │   (Automation)  │    │   Website       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File System   │    │   Playwright    │    │   Search API    │
│   (CSV/JSON)    │    │   Browser       │    │   Results       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

The system follows a modular architecture with clear separation of concerns:

**Frontend Layer (React)**
- User Interface Components
- File Upload Handlers  
- Real-time Progress Display
- Result Visualization
- Configuration Management

**Backend Layer (Python)**
- Automation Engine
- Browser Control (Playwright)
- Data Processing
- Result Analysis
- Export Generation

**Integration Layer**
- WebSocket/HTTP API for real-time communication
- File I/O for data import/export
- Browser automation for web scraping

## Components and Interfaces

### Frontend Components

#### 1. Main Application Container (`App.tsx`)
**Purpose:** Root component managing application state and layout
**Key Features:**
- Global state management for names, results, and configuration
- Layout orchestration
- Error boundary handling

**State Management:**
```typescript
interface AppState {
  names: string[];
  results: SearchResult[];
  isRunning: boolean;
  currentIndex: number;
  config: AutomationConfig;
  progress: ProgressInfo;
}
```

#### 2. Name Input Component (`NameInput.tsx`)
**Purpose:** Handle manual name entry and validation
**Features:**
- Text input with validation
- Add/remove individual names
- Bulk name management
- Input sanitization

**Interface:**
```typescript
interface NameInputProps {
  onNamesChange: (names: string[]) => void;
  existingNames: string[];
  disabled: boolean;
}
```

#### 3. File Import Component (`FileImport.tsx`)
**Purpose:** Handle CSV and JSON file imports
**Features:**
- Drag-and-drop file upload
- File format validation
- Preview imported data
- Error handling and user feedback

**Supported Formats:**
- CSV files with 'name' column or first column as names
- JSON arrays of strings
- JSON arrays of objects with 'name' property

#### 4. Automation Control Component (`AutomationControl.tsx`)
**Purpose:** Control automation execution and display progress
**Features:**
- Start/stop automation controls
- Real-time progress tracking
- Current search status display
- Estimated completion time

#### 5. Results Display Component (`ResultsDisplay.tsx`)
**Purpose:** Show search results with filtering and sorting
**Features:**
- Tabular results display
- Status-based filtering (Match/No Match/Error)
- Sorting by name, status, timestamp
- Export functionality

#### 6. Configuration Panel (`ConfigPanel.tsx`)
**Purpose:** Manage automation settings
**Features:**
- Delay configuration (1-10 seconds)
- Retry settings (1-5 attempts)
- Timeout configuration (10-60 seconds)
- Headless mode toggle

### Backend Components

#### 1. Automation Engine (`automation_engine.py`)
**Purpose:** Orchestrate the complete automation workflow
**Key Responsibilities:**
- Coordinate browser automation
- Manage search queue
- Handle retries and error recovery
- Generate progress updates

**Main Interface:**
```python
class AutomationEngine:
    async def run_automation(self, names: List[str], config: Config) -> AutomationResult
    async def stop_automation(self) -> None
    def get_progress(self) -> ProgressInfo
```

#### 2. Enhanced Browser Controller (`browser_controller.py`)
**Purpose:** Control browser interactions with ReadySearch
**Key Enhancements:**
- Updated URL targeting (`https://readysearch.com.au/products?person`)
- Improved search form handling
- Enhanced popup detection and dismissal
- Better error recovery mechanisms

**Search Flow:**
1. Navigate to person search page
2. Fill name input field
3. Handle optional birth year fields
4. Submit search form
5. Wait for results page
6. Handle any popups/modals

#### 3. Result Analyzer (`result_analyzer.py`)
**Purpose:** Analyze search results for exact name matches
**Key Features:**
- Parse ReadySearch results page structure
- Extract person names from results
- Perform exact name matching with normalization
- Handle multiple result formats

**Matching Logic:**
- Case-insensitive comparison
- Whitespace normalization
- Title/suffix removal (Mr., Mrs., Jr., etc.)
- Nickname handling (Bill/William, Bob/Robert)

#### 4. Real-time Communication (`websocket_handler.py`)
**Purpose:** Enable real-time updates between frontend and backend
**Features:**
- WebSocket connection management
- Progress update broadcasting
- Result streaming
- Error notification

#### 5. Enhanced Input Processor (`input_processor.py`)
**Purpose:** Process various input formats
**Supported Formats:**
- Manual name arrays
- CSV files (with/without headers)
- JSON arrays and objects
- Text file lists

### API Interfaces

#### WebSocket Events
```typescript
// Client to Server
interface ClientEvents {
  'start-automation': { names: string[], config: AutomationConfig };
  'stop-automation': {};
  'get-progress': {};
}

// Server to Client  
interface ServerEvents {
  'progress-update': ProgressInfo;
  'search-complete': SearchResult;
  'automation-finished': AutomationSummary;
  'error': ErrorInfo;
}
```

#### HTTP Endpoints
```
POST /api/upload-csv     - Upload CSV file
POST /api/upload-json    - Upload JSON file
GET  /api/results        - Get current results
GET  /api/export-csv     - Export results as CSV
GET  /api/export-json    - Export results as JSON
POST /api/config         - Update configuration
```

## Data Models

### Core Data Structures

```typescript
interface SearchResult {
  name: string;
  status: 'Match' | 'No Match' | 'Error' | 'Pending';
  timestamp?: string;
  error?: string;
  matchDetails?: MatchInfo[];
  searchDuration?: number;
}

interface MatchInfo {
  foundName: string;
  confidence: number;
  source: string;
  additionalData?: any;
}

interface AutomationConfig {
  delayBetweenSearches: number;    // 1-10 seconds
  maxRetries: number;              // 1-5 attempts
  searchTimeout: number;           // 10-60 seconds
  headlessMode: boolean;
  enableScreenshots: boolean;
}

interface ProgressInfo {
  currentIndex: number;
  totalNames: number;
  completedSearches: number;
  successfulMatches: number;
  errors: number;
  estimatedTimeRemaining: number;
  currentSearchName?: string;
}
```

### Database Schema (Optional - for persistence)

```sql
-- Results storage for large datasets
CREATE TABLE search_sessions (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP,
  total_names INTEGER,
  completed_names INTEGER,
  status VARCHAR(20)
);

CREATE TABLE search_results (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES search_sessions(id),
  name VARCHAR(255),
  status VARCHAR(20),
  timestamp TIMESTAMP,
  error_message TEXT,
  match_data JSONB
);
```

## Error Handling

### Error Categories and Responses

#### 1. Network Errors
- **Timeout errors:** Retry with exponential backoff
- **Connection failures:** Pause automation, notify user
- **Rate limiting:** Implement respectful delays

#### 2. Browser Errors  
- **Page load failures:** Retry navigation
- **Element not found:** Try alternative selectors
- **Browser crashes:** Restart browser, resume from last position

#### 3. Input Validation Errors
- **Invalid file formats:** Show specific error messages
- **Empty/malformed data:** Skip invalid entries, report count
- **Name validation:** Sanitize input, warn about special characters

#### 4. ReadySearch Website Changes
- **Layout changes:** Fallback selector strategies
- **New popup types:** Expandable popup handler patterns
- **API changes:** Graceful degradation with user notification

### Error Recovery Strategies

```python
class ErrorRecoveryManager:
    async def handle_search_error(self, error: Exception, context: SearchContext) -> RecoveryAction:
        if isinstance(error, TimeoutError):
            return RecoveryAction.RETRY_WITH_DELAY
        elif isinstance(error, ElementNotFoundError):
            return RecoveryAction.TRY_ALTERNATIVE_SELECTORS
        elif isinstance(error, BrowserCrashError):
            return RecoveryAction.RESTART_BROWSER
        else:
            return RecoveryAction.SKIP_AND_CONTINUE
```

## Testing Strategy

### Unit Testing
- **Frontend:** Jest + React Testing Library
- **Backend:** pytest with async support
- **Components:** Individual component testing
- **Utilities:** Name matching, file processing, validation

### Integration Testing
- **API endpoints:** Full request/response cycle testing
- **WebSocket communication:** Real-time event testing
- **File processing:** End-to-end import/export testing

### End-to-End Testing
- **Automation workflow:** Complete search automation testing
- **Browser interaction:** Playwright-based testing
- **Error scenarios:** Simulated failure testing

### Performance Testing
- **Large dataset handling:** 1000+ names processing
- **Memory usage:** Long-running automation monitoring
- **Browser resource management:** Memory leak detection

### Test Data and Mocking
```python
# Mock ReadySearch responses for testing
MOCK_SEARCH_RESPONSES = {
    'john_smith': {
        'status': 'success',
        'results': [
            {'name': 'John Smith', 'location': 'Sydney NSW'},
            {'name': 'John A Smith', 'location': 'Melbourne VIC'}
        ]
    },
    'no_results': {
        'status': 'success', 
        'results': []
    }
}
```

## Security Considerations

### Data Protection
- **Input sanitization:** Prevent XSS and injection attacks
- **File upload validation:** Restrict file types and sizes
- **Data encryption:** Encrypt sensitive search data at rest

### Rate Limiting and Compliance
- **Respectful automation:** 2.5-second delays between requests
- **User-Agent rotation:** Realistic browser identification
- **Terms of service compliance:** Respect ReadySearch policies

### Privacy
- **Data retention:** Configurable result storage duration
- **Export security:** Secure file download mechanisms
- **Logging:** Avoid logging sensitive personal information

## Performance Optimization

### Frontend Optimization
- **Virtual scrolling:** Handle large result sets efficiently
- **Debounced inputs:** Reduce unnecessary re-renders
- **Lazy loading:** Load components on demand
- **Memoization:** Cache expensive computations

### Backend Optimization
- **Connection pooling:** Reuse browser instances
- **Batch processing:** Group operations for efficiency
- **Memory management:** Clean up resources promptly
- **Caching:** Cache common search patterns

### Scalability Considerations
- **Horizontal scaling:** Support multiple browser instances
- **Queue management:** Handle large search queues
- **Resource monitoring:** Track CPU, memory, and network usage
- **Graceful degradation:** Maintain functionality under load

## Deployment Architecture

### Development Environment
```
Frontend: React Dev Server (localhost:3000)
Backend: Python FastAPI (localhost:8000)
Browser: Playwright Chromium (headed mode for debugging)
```

### Production Environment
```
Frontend: Nginx serving static React build
Backend: Gunicorn + FastAPI behind reverse proxy
Browser: Headless Chromium in Docker container
Database: PostgreSQL for result persistence (optional)
```

### Docker Configuration
```dockerfile
# Multi-stage build for production deployment
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.11 AS backend
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
COPY . .
COPY --from=frontend-build /app/frontend/dist ./static

EXPOSE 8000
CMD ["gunicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

This design provides a robust, scalable, and user-friendly solution for automating ReadySearch.com.au name searches while maintaining high performance and reliability standards.