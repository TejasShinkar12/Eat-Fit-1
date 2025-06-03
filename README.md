# PantryFit

A smart fitness and inventory management application that helps users track their food inventory, monitor nutritional intake, and generate healthy recipes based on available ingredients.

## Features

- User authentication and profile management
- Image-based inventory ingestion using ML
- Manual inventory management
- Calorie and macronutrient tracking
- Recipe generation based on available ingredients
- Weekly reports and alerts

## Tech Stack

- **Frontend**: React with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ML Services**: 
  - Image Processing (Object Detection + OCR)
  - Recipe Generation
  - Text Q&A

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- PostgreSQL

### Frontend Setup

```bash
cd src/frontend
npm install
npm start
```

### Backend Setup

```bash
cd src/backend
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/pantryfit
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

- Frontend runs on `http://localhost:3000`
- Backend API runs on `http://localhost:8000`
- API documentation available at `http://localhost:8000/docs`

## Testing

### Frontend Tests
```bash
cd src/frontend
npm test
```

### Backend Tests
```bash
cd src/backend
pytest
```

## Project Structure

```
src/
├── frontend/           # React TypeScript application
├── backend/           # FastAPI application
├── ml_services/       # Machine Learning services
└── shared/           # Shared utilities and types
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 