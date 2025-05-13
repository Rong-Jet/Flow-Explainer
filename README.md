# Flow Explainer

A web application that generates Mermaid diagrams from JSON files using AI interpretation.

## Project Structure

- **Frontend**: React application for uploading JSON files and displaying generated diagrams
- **Backend**: Django application with LangGraph integration for processing JSON and generating diagrams

## Setup Instructions

### Prerequisites

- Node.js and npm
- Python 3.8+
- uv (Python package installer) - Install with `pip install uv`
- OpenAI API key

### Environment Setup

1. Navigate to the backend directory and copy the environment template file:
   ```
   cd backend
   cp .env.template .env
   ```

2. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

   Without this key, the application will not function correctly. The backend will display detailed instructions if the key is missing.

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create and activate a virtual environment using uv:
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies using the uv.lock file (for exact dependency versions):
   ```
   uv sync
   ```
   
   Alternatively, if you just want to install from requirements.txt:
   ```
   uv pip install -r requirements.txt
   ```

4. Start the Django server:
   ```
   cd django_app
   python manage.py runserver
   ```
   The server will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the project root:
   ```
   cd Flow-Explainer
   ```

2. Install npm dependencies:
   ```
   npm install
   ```

3. Start the React development server:
   ```
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Upload a JSON file using the frontend interface
2. The file will be sent to the Django backend
3. Django uses LangGraph to process the JSON:
   - Validates the JSON structure
   - Converts the JSON to Mermaid diagram syntax
   - Renders the diagram as SVG
4. The diagram is returned to the frontend for display

## Features

- Upload and validate JSON files
- Convert JSON to Mermaid diagram syntax using AI
- Render the diagram in the browser
- View the generated Mermaid code
- Download the diagram as SVG 

## Architecture

The application uses LangGraph, an agent-based system built on LangChain, to process the JSON files. The workflow consists of these steps:

1. **Validation**: Checks if the JSON is valid and not too large
2. **Mermaid Code Generation**: Converts the JSON structure to Mermaid syntax
3. **Diagram Rendering**: Generates an SVG from the Mermaid code

## Security Considerations

For development, the application uses relaxed security settings to facilitate local testing. When deploying to production, you should:

1. Update CORS settings in `backend/django_app/mermaid_diagram/settings.py`:
   - Set specific allowed origins instead of allowing all origins
   - Uncomment and configure the security middleware settings

2. Set up HTTPS:
   - Configure SSL certificates
   - Enable secure cookie settings
   - Enable HSTS for enhanced security

3. API key management:
   - The application uses a `.env` file for storing sensitive information like API keys
   - Never commit the `.env` file to the repository (it's included in .gitignore)
   - In production, consider using a secure secrets management system instead of .env files

4. Rate limiting:
   - Consider implementing rate limiting to prevent abuse

## Error Handling

The application provides detailed error messages to help diagnose issues:

- JSON validation errors (size limits, format issues)
- Diagram generation problems (complex structures, unsupported features)
- Rendering errors (syntax issues in the generated diagram code)

Error messages include both user-friendly explanations and technical details to assist with troubleshooting. 