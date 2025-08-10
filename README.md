# FitEats

A smart fitness and inventory management mobile application that helps users track their food inventory, monitor nutritional intake, and generate healthy recipes based on available ingredients.

## Features

- User authentication and profile management
- Image-based inventory ingestion using ML
- Manual inventory management
- Calorie and macronutrient tracking
- Recipe generation based on available ingredients (using GEMINI API)
- Weekly reports and alerts
- Basic text Q&A functionality

## Tech Stack

- **Frontend**: React Native with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ML Services**: 
  - Image Processing (Object Detection + OCR using Detectron2 & TrOCR)
  - Recipe Generation (GEMINI API via LangChain)
  - Text Q&A
- **Authentication**: JWT-based with bcrypt password hashing

## Project Structure

```
.
├── docs/                   # Project documentation
│   ├── requirements.md     # Project requirements
│   ├── prd.md             # Product specification
│   ├── techstack.md       # Technical decisions
│   ├── backend.md         # Backend implementation guide
│   ├── frontend.md        # Frontend implementation guide
│   ├── flow.md            # System and user flows
│   └── status.md          # Progress tracking
├── src/
│   ├── frontend/          # React Native application
│   ├── backend/           # FastAPI application
│   ├── ml_services/       # Machine Learning services
│   │   ├── image_processing/
│   │   ├── recipe_generation/
│   │   └── text_qa/
│   └── shared/           # Shared utilities and types
├── tests/                # Test suites
└── scripts/             # Utility scripts
```

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- PostgreSQL
- Git
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

### Frontend Setup

```bash
cd src/frontend
npm install
# For iOS (macOS only)
cd ios && pod install && cd ..
# Start Metro bundler
npm start
# In a new terminal, run the app
# For iOS (macOS only)
npm run ios
# For Android
npm run android
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
DATABASE_URL=postgresql://user:password@localhost:5432/fiteats
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

- Backend API runs on `http://localhost:8000`
- API documentation available at `http://localhost:8000/docs`
- Follow the implementation guides in the `docs/` directory
- Keep `status.md` updated with your progress

### Development Workflow

1. Read through the documentation in `docs/` to understand requirements
2. Follow the PRD step by step for implementation
3. Keep the project structure organized
4. Update status.md after completing each step
5. Ask for clarification when requirements are unclear

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

## Documentation

- `requirements.md`: Source of truth for project requirements
- `prd.md`: Product specification and features
- `techstack.md`: Technical decisions and architecture
- `backend.md`: Backend implementation guide
- `frontend.md`: Frontend implementation guide
- `flow.md`: System and user flow documentation
- `status.md`: Progress tracking and milestones

## Contributing

1. Read all documentation files before starting implementation
2. Follow the PRD step by step
3. Keep the project structure organized
4. Update status.md after completing each step
5. Write clear comments and documentation
6. Follow the defined architecture
7. Test thoroughly before marking tasks complete

## License

This project is licensed under the MIT License - see the LICENSE file for details. 