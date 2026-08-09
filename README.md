# DevPulse

DevPulse is a full-stack application built with a Python backend and a React/Vite frontend. It includes a worker component and is configured for deployment on Zerops.

## Project Structure

- **frontend/**: The user interface, built using React and Vite.
- **backend/**: The main API service, built in Python.
- **worker/**: Background worker service.
- **zerops.yaml**: Configuration file for deploying to the Zerops platform.

## Getting Started

### Prerequisites
- Node.js (for frontend)
- Python 3 (for backend and worker)

### Frontend Setup
Navigate to the `frontend` directory and install dependencies:
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
Navigate to the `backend` directory, create a virtual environment, and install dependencies:
```bash
cd backend
python -m venv venv
# Activate the virtual environment
# Windows: venv\Scripts\activate
# Unix/MacOS: source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Deployment
This project is configured to be deployed on [Zerops](https://zerops.io/). See the `zerops.yaml` file for the deployment pipeline configuration.
