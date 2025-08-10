# Backend Implementation Guide: Fitness Inventory & Recipe App MVP

**Version:** 1.0
**Date:** May 25, 2024

## 1. API Design

This section outlines the key RESTful API endpoints for the backend, built using FastAPI. Payloads are described using implied Pydantic models for clarity.

**Base URL:** `/api/v1` (implicitly used in endpoint paths below)

### 1. User Authentication & Profile

*   **`POST /auth/signup`**
    *   **Description:** Registers a new user.
    *   **Request Body:** `{ "email": "...", "password": "...", "height": ..., "weight": ..., "age": ..., "sex": "male/female", "activity_level": "low/moderate/high", "fitness_goal": "gain/lose/maintain" }`
    *   **Response:** `{ "access_token": "...", "token_type": "bearer" }`
    *   **Status Codes:** 200 OK, 400 Bad Request (e.g., email already exists)
*   **`POST /auth/login`**
    *   **Description:** Logs in an existing user.
    *   **Request Body:** `{ "email": "...", "password": "..." }`
    *   **Response:** `{ "access_token": "...", "token_type": "bearer" }`
    *   **Status Codes:** 200 OK, 401 Unauthorized (invalid credentials)
*   **`GET /users/me`**
    *   **Description:** Get the authenticated user's profile.
    *   **Authentication:** Required
    *   **Request:** None
    *   **Response:** `{ "email": "...", "height": ..., "weight": ..., "age": ..., "sex": "...", "activity_level": "...", "fitness_goal": "...", "bmr": ..., "tdee": ... }` (Includes calculated BMR/TDEE)
    *   **Status Codes:** 200 OK, 401 Unauthorized
*   **`PUT /users/me`**
    *   **Description:** Update the authenticated user's profile.
    *   **Authentication:** Required
    *   **Request Body:** `{ "height": ..., "weight": ..., "age": ..., "activity_level": "...", "fitness_goal": "..." }` (Partial updates allowed)
    *   **Response:** `{ "email": "...", "height": ..., "weight": ..., "age": ..., "sex": "...", "activity_level": "...", "fitness_goal": "...", "bmr": ..., "tdee": ... }`
    *   **Status Codes:** 200 OK, 400 Bad Request, 401 Unauthorized

### 2. Inventory Management

*   **`POST /inventory/upload-image`**
    *   **Description:** Uploads an image for inventory ingestion.
    *   **Authentication:** Required
    *   **Request Body:** `form-data` containing a `file` field (the image).
    *   **Response:** `{ "message": "Image upload initiated. Processing in background." }` (Actual items will appear later)
    *   **Status Codes:** 200 OK, 400 Bad Request, 401 Unauthorized, 500 Internal Server Error (if processing setup fails)
*   **`GET /inventory`**
    *   **Description:** Lists all inventory items for the authenticated user.
    *   **Authentication:** Required
    *   **Request:** Optional query parameters: `name` (search), `expires_soon` (boolean), etc.
    *   **Response:** `[ { "id": ..., "name": "...", "quantity": ..., "calories_per_serving": ..., "protein_g_per_serving": ..., "carbs_g_per_serving": ..., "fats_g_per_serving": ..., "expiry_date": "YYYY-MM-DD" }, ... ]`
    *   **Status Codes:** 200 OK, 401 Unauthorized
*   **`POST /inventory`**
    *   **Description:** Adds a new inventory item manually.
    *   **Authentication:** Required
    *   **Request Body:** `{ "name": "...", "quantity": ..., "calories_per_serving": ..., "protein_g_per_serving": ..., "carbs_g_per_serving": ..., "fats_g_per_serving": ..., "expiry_date": "YYYY-MM-DD" }`
    *   **Response:** `{ "id": ..., "name": "...", ... }` (The created item)
    *   **Status Codes:** 201 Created, 400 Bad Request, 401 Unauthorized
*   **`GET /inventory/{item_id}`**
    *   **Description:** Get a specific inventory item by ID.
    *   **Authentication:** Required
    *   **Request:** Path parameter `item_id`.
    *   **Response:** `{ "id": ..., "name": "...", ... }`
    *   **Status Codes:** 200 OK, 401 Unauthorized, 404 Not Found
*   **`PUT /inventory/{item_id}`**
    *   **Description:** Update a specific inventory item by ID.
    *   **Authentication:** Required
    *   **Request:** Path parameter `item_id`. Request Body: `{ "name": "...", "quantity": ..., ... }` (Partial updates allowed)
    *   **Response:** `{ "id": ..., "name": "...", ... }` (The updated item)
    *   **Status Codes:** 200 OK, 400 Bad Request, 401 Unauthorized, 404 Not Found
*   **`DELETE /inventory/{item_id}`**
    *   **Description:** Delete a specific inventory item by ID.
    *   **Authentication:** Required
    *   **Request:** Path parameter `item_id`.
    *   **Response:** `{ "message": "Item deleted successfully" }`
    *   **Status Codes:** 200 OK, 401 Unauthorized, 404 Not Found
*   **`POST /inventory/{item_id}/consume`**
    *   **Description:** Marks a quantity of an item as consumed, creating a consumption log entry.
    *   **Authentication:** Required
    *   **Request:** Path parameter `item_id`. Request Body: `{ "quantity": ... }`
    *   **Response:** `{ "consumption_log_id": ..., "consumed_quantity": ..., "calories": ..., ... }`
    *   **Status Codes:** 201 Created, 400 Bad Request (e.g., quantity exceeds available), 401 Unauthorized, 404 Not Found

### 3. Calorie Tracking

*   **`GET /tracker/daily`**
    *   **Description:** Get today's consumption summary for the authenticated user.
    *   **Authentication:** Required
    *   **Request:** None
    *   **Response:** `{ "date": "YYYY-MM-DD", "target_calories": ..., "consumed_calories": ..., "consumed_protein_g": ..., "consumed_carbs_g": ..., "consumed_fats_g": ..., "inventory_depletion_log": [ { "item_name": "...", "quantity": ..., "timestamp": "..." }, ... ] }`
    *   **Status Codes:** 200 OK, 401 Unauthorized

### 4. Recipe Generator

*   **`POST /recipes/generate-from-inventory`**
    *   **Description:** Generates a recipe based on current inventory and user goal using GEMINI API.
    *   **Authentication:** Required
    *   **Request:** None (uses current inventory)
    *   **Response:** `{ "title": "...", "ingredients": ["...", "..."], "directions": "..." }`
    *   **Status Codes:** 200 OK, 400 Bad Request, 401 Unauthorized, 500 Internal Server Error (if GEMINI API fails)

### 5. Reports & Alerts

*   **`GET /reports/weekly-nutrients`**
    *   **Description:** Get aggregated nutrient consumption for the past 7 days.
    *   **Authentication:** Required
    *   **Request:** None
    *   **Response:** `[ { "date": "YYYY-MM-DD", "calories": ..., "protein_g": ..., "carbs_g": ..., "fats_g": ... }, ... ]` (One object per day)
    *   **Status Codes:** 200 OK, 401 Unauthorized
*   **`GET /reports/top-contributors`**
    *   **Description:** Get items that contributed most to calorie/macro intake over the past week.
    *   **Authentication:** Required
    *   **Request:** Optional query parameter `period` (default: 7 days).
    *   **Response:** `[ { "item_name": "...", "total_calories_consumed": ..., "total_quantity_consumed": ... }, ... ]` (Ordered by calories)
    *   **Status Codes:** 200 OK, 401 Unauthorized
*   **`GET /alerts`**
    *   **Description:** Get active alerts for the user (expiry, calorie deviation).
    *   **Authentication:** Required
    *   **Request:** None
    *   **Response:** `[ { "type": "expiry", "message": "...", "item_id": "..." }, { "type": "calorie_intake", "message": "..." }, ... ]`
    *   **Status Codes:** 200 OK, 401 Unauthorized

### 6. Basic Voice & Text Q&A (Text-only MVP)

*   **`POST /qa`**
    *   **Description:** Processes a text query about inventory or consumption.
    *   **Authentication:** Required
    *   **Request Body:** `{ "query": "What's in my fridge?" }`
    *   **Response:** `{ "answer": "..." }`
    *   **Status Codes:** 200 OK, 400 Bad Request, 401 Unauthorized

## 2. Data Models

Using PostgreSQL, we'll define tables corresponding to the core entities. An ORM like SQLAlchemy is recommended for interacting with the database from FastAPI.

```sql
-- users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    height DECIMAL, -- in cm or inches
    weight DECIMAL, -- in kg or lbs
    age INTEGER,
    sex VARCHAR(10), -- 'male', 'female'
    activity_level VARCHAR(20), -- 'low', 'moderate', 'high'
    fitness_goal VARCHAR(20), -- 'gain', 'lose', 'maintain'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- inventory table
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    quantity DECIMAL DEFAULT 1, -- Number of servings/items
    calories_per_serving DECIMAL,
    protein_g_per_serving DECIMAL,
    carbs_g_per_serving DECIMAL,
    fats_g_per_serving DECIMAL,
    expiry_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- consumption_log table
CREATE TABLE consumption_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    inventory_item_id INTEGER REFERENCES inventory(id) ON DELETE SET NULL, -- If item is deleted, log remains
    item_name_snapshot VARCHAR(255), -- Store name at time of consumption
    quantity_consumed DECIMAL NOT NULL,
    calories_consumed DECIMAL,
    protein_consumed DECIMAL,
    carbs_consumed DECIMAL,
    fats_consumed DECIMAL,
    consumed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- generated_recipes table
CREATE TABLE generated_recipes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    ingredients JSONB NOT NULL, -- Store as JSON array
    directions TEXT NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Indexing:**
*   Add indexes on `user_id` in `inventory` and `consumption_log` for efficient filtering by user.
*   Index `email` in `users` for quick lookups during login.
*   Index `consumed_at` in `consumption_log` for time-based queries (daily, weekly reports).
*   Index `expiry_date` in `inventory` for alert queries.

## 3. Business Logic

### 3.1 User Authentication & Profile
*   **Signup:**
    *   Receive user data.
    *   Check if email already exists.
    *   Hash the user's password using a strong algorithm (e.g., bcrypt).
    *   Store user details (including hashed password) in the `users` table.
    *   Generate a JWT for the user.
    *   Return the JWT.
*   **Login:**
    *   Receive email and password.
    *   Retrieve user from `users` table by email.
    *   Verify the provided password against the stored hash.
    *   If valid, generate and return a JWT. If invalid, return 401.
*   **Profile:**
    *   Get user ID from the authenticated JWT.
    *   Retrieve user data from the `users` table.
    *   Calculate BMR (Basal Metabolic Rate) using a standard formula (e.g., Mifflin-St Jeor or Harris-Benedict) based on age, sex, height, weight.
    *   Calculate TDEE (Total Daily Energy Expenditure) by multiplying BMR by an activity level factor (e.g., 1.2 for low, 1.55 for moderate, 1.9 for high).
    *   Return profile data including calculated BMR/TDEE.
*   **Update Profile:**
    *   Get user ID from the authenticated JWT.
    *   Receive updated profile data.
    *   Validate input.
    *   Update the corresponding fields in the `users` table for that user.
    *   Recalculate and return BMR/TDEE in the response.

### 3.2 Inventory Ingestion via Image
*   **Image Upload:**
    *   Receive the image file via the API endpoint.
    *   Save the image temporarily or pass its byte stream directly to the processing pipeline initiation function.
    *   Return an immediate "processing initiated" response to the frontend.
    *   **Background Task:** The heavy lifting should happen in a background task (FastAPI's `BackgroundTasks`, Celery worker, or similar).
        1.  Load the Detectron2-based object detection model.
        2.  Run object detection on the image to identify potential food item bounding boxes.
        3.  For each detected bounding box:
            *   Crop the image region.
            *   Attempt to identify the nutrition label area within the crop (can be challenging, might require heuristics or a secondary model).
            *   If a label area is identified, apply the TrOCR model to extract text.
            *   Parse the extracted text using regex and keyword matching to find "Calories", "Protein", "Carbohydrates", "Fat", serving size info, and potentially expiry dates. This parsing step is complex and error-prone; robustness requires careful implementation.
            *   Attempt to identify the item name (e.g., near the top or on the main packaging).
            *   Structure the extracted/parsed data: `name`, `calories_per_serving`, `protein_g_per_serving`, `carbs_g_per_serving`, `fats_g_per_serving`, `expiry_date`. Defaults: `quantity=1`.
        4.  For each successfully parsed item:
            *   Validate the extracted nutritional data (e.g., numbers make sense).
            *   Create a new entry in the `inventory` table associated with the user.
        5.  Log any items that couldn't be processed or parsed correctly for potential manual review (optional for MVP).

### 3.3 Inventory View & Manual Edits
*   **List Inventory:**
    *   Get user ID from JWT.
    *   Query the `inventory` table for all items belonging to that user.
    *   Apply optional filters (e.g., search by name, filter by expiry date).
    *   Return the list of items.
*   **Add/Edit/Delete:**
    *   Implement standard CRUD operations for the `inventory` table.
    *   Ensure that only items owned by the authenticated user can be accessed/modified/deleted.
*   **Mark Consumed:**
    *   Get user ID from JWT.
    *   Receive `item_id` and `quantity` consumed.
    *   Retrieve the `inventory` item by ID, verifying it belongs to the user.
    *   Calculate total calories, protein, carbs, and fats consumed based on the item's per-serving data and the consumed quantity.
    *   Create a new entry in the `consumption_log` table, linking to the item (or just snapshotting its name and nutritional value), user, consumed quantity, calculated nutrition totals, and timestamp.
    *   *(Optional for MVP calorie tracking, but good for inventory accuracy):* Decrement the quantity of the item in the `inventory` table. If quantity reaches 0 or less, consider deleting or marking the item as depleted.

### 3.4 Fitness Profile-Based Calorie Tracking
*   **Daily Tracking:**
    *   Get user ID from JWT.
    *   Retrieve the user's TDEE (either calculate it or fetch if stored).
    *   Query the `consumption_log` table for entries belonging to the user for the current day (based on `consumed_at` timestamp).
    *   Aggregate (SUM) the `calories_consumed`, `protein_consumed`, `carbs_consumed`, and `fats_consumed` from these log entries.
    *   Retrieve inventory depletion logs (items consumed today) from `consumption_log` and potentially `inventory` history.
    *   Return the TDEE, total consumed calories/macros, and the depletion log for the day.

### 3.5 Recipe Generator
*   **Recipe Generation with GEMINI API:**
    *   Get user ID from JWT.
    *   Retrieve the user's current inventory items (or use specific items provided in the request). Filter out items with quantity 0 or expired if desired.
    *   Get the user's fitness goal from their profile.
    *   Format a structured prompt for the GEMINI API that includes:
        *   A clear instruction to generate a recipe.
        *   The list of available inventory items (e.g., "Using: chicken breast, broccoli, quinoa, olive oil").
        *   The user's fitness goal (gain/lose/maintain), framed as a constraint (e.g., "Generate a healthy recipe for someone trying to lose weight").
        *   Structured output format instructions using Pydantic schema for recipe title, ingredients list, and directions.
    *   Send the prompt to the GEMINI API through LangChain with PydanticOutputParser for structured response parsing.
    *   Receive and parse the structured response from the API into distinct "title", "ingredients" and "instructions" sections.
    *   Save the generated recipe in the `generated_recipes` table.

### 3.6 Reports & Alerts
*   **Weekly Nutrient Trend:**
    *   Get user ID from JWT.
    *   Query `consumption_log` for the last 7 days (or specified period) for the user.
    *   Group the results by day and sum the consumed calories/macros for each day.
    *   Return the daily aggregates.
*   **Top Contributors:**
    *   Get user ID from JWT.
    *   Query `consumption_log` for a specific period (e.g., last 7 days) for the user.
    *   Join with the `inventory` table (or use the `item_name_snapshot`).
    *   Group by item name/ID and sum the `calories_consumed` and `quantity_consumed`.
    *   Order by total calories consumed.
    *   Return the list of items.
*   **Alerts:**
    *   Get user ID from JWT.
    *   **Expiry Alert:** Query `inventory` for the user's items where `expiry_date` is not null and is within the next 2 days. Generate alert messages for these items.
    *   **Calorie Alert:** Calculate today's consumed calories. Compare against the user's TDEE and fitness goal. If significantly outside a reasonable range (e.g., < BMR for weight loss, far below TDEE for gain), generate a calorie intake alert. Thresholds need definition.
    *   Combine and return the active alerts.

### 3.7 Basic Voice & Text Q&A
*   **Process Query:**
    *   Get user ID from JWT.
    *   Receive the text query.
    *   Use simple keyword matching or a small intent classification layer to understand the query type (e.g., "inventory", "protein today").
    *   Based on intent, execute the corresponding backend logic/database query (e.g., if "inventory", call the `GET /inventory` logic; if "protein today", query `consumption_log` for today's protein sum).
    *   Format the result into a simple text answer.
    *   Return the answer.

## 4. Security

*   **Authentication:** Implement JWT-based authentication.
    *   Upon successful login/signup, issue a short-lived access token and potentially a longer-lived refresh token (for MVP, access token might suffice).
    *   Tokens should be signed with a strong secret key stored securely (environment variable).
    *   Frontend sends the access token in the `Authorization: Bearer <token>` header for protected routes.
    *   FastAPI dependency injection (`Depends(oauth2_scheme)`) verifies the token and extracts the user ID for each protected request.
*   **Authorization:** Crucially, ensure Row-Level Security.
    *   Every database query and operation that accesses user data (`inventory`, `consumption_log`, `recipes`, `users` when updating) *must* filter results or target rows using the authenticated user's ID (`WHERE user_id = current_user_id`). Never trust user-provided IDs for accessing data without validating ownership.
*   **Password Hashing:** Store only bcrypt (or similar) hashes of user passwords in the `users` table. Use a standard library (e.g., `passlib`) for hashing and verification.
*   **Input Validation:** Use FastAPI's Pydantic models for automatic request body and query parameter validation to prevent many common web vulnerabilities.
*   **API Keys:** Store Hugging Face API keys and database credentials securely using environment variables, not directly in code.
*   **HTTPS:** Deploy the backend using HTTPS in production to encrypt data in transit.
*   **Rate Limiting:** Consider adding basic rate limiting on authentication endpoints to prevent brute-force attacks (optional for MVP).

## 5. Performance

*   **Database Indexing:** As mentioned in Data Models, add indexes on frequently queried columns (`user_id`, `email`, `consumed_at`, `expiry_date`) to speed up database reads.
*   **Image Processing Offloading:** This is the most performance-critical part. Use background tasks (e.g., FastAPI's own `BackgroundTasks`, or a dedicated task queue like Celery with Redis/RabbitMQ) to handle image analysis asynchronously. The user gets an immediate response, and the inventory updates later.
*   **Model Loading:** For the GEMINI API, connection pooling and efficient prompt engineering help with performance.
*   **Hugging Face Inference:** No longer needed for recipe generation as we're using GEMINI API.
*   **Caching (Optional MVP):** Use Redis to cache results of frequent read queries, such as:
    *   A user's current inventory list.
    *   Today's calorie tracking summary.
    *   Recently generated recipes.
*   **Query Optimization:** Monitor slow database queries and optimize them using SQL query analysis tools (`EXPLAIN ANALYZE`).
*   **Scalability:** For future growth, design the application to be stateless (except for the database), allowing for horizontal scaling by running multiple FastAPI instances behind a load balancer. Containerization (Docker) facilitates this.

## 6. Code Examples

These examples demonstrate key concepts using FastAPI, Pydantic, and a placeholder for database interaction (assuming an ORM like SQLAlchemy).

```python
# 6.1 Basic Authentication Endpoints (Signup & Login)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# --- Configuration (Use environment variables in production) ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY" # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- JWT Handling ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- FastAPI Setup ---
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Placeholder for DB interaction (replace with SQLAlchemy session)
class MockDB:
    def __init__(self):
        self.users = {} # email -> user_data

    def get_user_by_email(self, email: str):
        return self.users.get(email)

    def create_user(self, user_data: dict):
        if user_data['email'] in self.users:
            return None # User already exists
        self.users[user_data['email']] = user_data
        # In real DB, generate ID, hash password, etc.
        user_data['id'] = len(self.users) # Mock ID
        user_data['hashed_password'] = get_password_hash(user_data['password'])
        del user_data['password'] # Don't store plain password
        return user_data

db = MockDB() # Use a real DB session manager in production

# --- Pydantic Models ---
class UserSignup(BaseModel):
    email: str
    password: str
    height: float
    weight: float
    age: int
    sex: str
    activity_level: str
    fitness_goal: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
    id: int
    email: str
    hashed_password: str
    height: float
    weight: float
    age: int
    sex: str
    activity_level: str
    fitness_goal: str

# --- Dependency to get current user ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # In real app, query user from DB using email/ID in payload
        user = db.get_user_by_email(email) # Mock DB lookup
        if user is None:
            raise credentials_exception
        # Return Pydantic model for typing benefits
        return UserInDB(**user) # Mock conversion
    except JWTError:
        raise credentials_exception

# --- Auth Endpoints ---
@app.post("/api/v1/auth/signup", response_model=Token)
async def signup(user: UserSignup):
    # In real app, use DB session
    db_user = db.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # In real app, create user in DB
    new_user_data = user.model_dump() # Pydantic V2
    created_user = db.create_user(new_user_data) # Handles hashing password

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": created_user['email'], "id": created_user['id']}, # Include user ID in token
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In real app, query user from DB
    user = db.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email'], "id": user['id']},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Example Protected Endpoint ---
@app.get("/api/v1/users/me")
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    # In real app, fetch full profile data + calculate BMR/TDEE
    # Mocking the response structure
    return {
        "email": current_user.email,
        "height": current_user.height,
        "weight": current_user.weight,
        "age": current_user.age,
        "sex": current_user.sex,
        "activity_level": current_user.activity_level,
        "fitness_goal": current_user.fitness_goal,
        "bmr": 1500, # Placeholder calculation
        "tdee": 2000 # Placeholder calculation
    }
```

```python
# 6.2 Inventory Ingestion (Conceptual Outline with Background Task)
from fastapi import UploadFile, File, BackgroundTasks, HTTPException
# Assume necessary imports for DB models and image processing functions

# Placeholder functions for image processing (need actual implementation)
def process_image_for_inventory(image_bytes: bytes, user_id: int):
    """
    This function runs the image processing pipeline.
    It should:
    1. Load models (Detectron2, TrOCR)
    2. Detect objects/labels
    3. Perform OCR
    4. Parse nutrition data
    5. Save results to the database for the given user_id
    This should run IN A SEPARATE PROCESS or worker.
    """
    print(f"Starting image processing for user {user_id}...")
    # --- Placeholder Logic ---
    try:
        # Simulate processing time
        import time
        time.sleep(5)
        print("Image processing finished.")
        # Simulate detected items
        detected_items = [
            {"name": "Granola Bar", "quantity": 2, "calories_per_serving": 180, "protein_g_per_serving": 5, "carbs_g_per_serving": 25, "fats_g_per_serving": 8, "expiry_date": "2024-12-01"},
            {"name": "Canned Beans", "quantity": 3, "calories_per_serving": 120, "protein_g_per_serving": 7, "carbs_g_per_serving": 20, "fats_g_per_serving": 0.5},
        ]
        # In real app, save these to inventory table for user_id
        print(f"Simulating saving {len(detected_items)} items to DB.")
        # Example of saving (replace with ORM calls):
        # for item_data in detected_items:
        #     new_item = Inventory(user_id=user_id, **item_data)
        #     db_session.add(new_item)
        # db_session.commit()

    except Exception as e:
        print(f"Error during image processing: {e}")
        # Log the error, potentially notify user (more advanced)

# Endpoint
@app.post("/api/v1/inventory/upload-image")
async def upload_inventory_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: UserInDB = Depends(get_current_user) # Get authenticated user
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read file content
    image_bytes = await file.read()

    # Add the processing task to the background queue
    # In a real system, you'd pass this to a task queue like Celery
    # For simple BackgroundTasks, the processing runs in the event loop
    # For heavy tasks, use a separate process or worker!
    background_tasks.add_task(process_image_for_inventory, image_bytes, current_user.id)

    return {"message": "Image upload received and processing initiated."}

```

```python
# 6.3 Log Consumption Example
# Assume DB models (Inventory, ConsumptionLog, User) and DB session dependency exist
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

# Placeholder Pydantic model for input
class ConsumeItem(BaseModel):
    quantity: float

# Placeholder DB session dependency (replace with actual)
def get_db_session():
    # yield SessionLocal()
    pass # Replace with real session manager

# Endpoint
@app.post("/api/v1/inventory/{item_id}/consume")
async def consume_item(
    item_id: int,
    consumption_data: ConsumeItem,
    current_user: UserInDB = Depends(get_current_user), # Authenticated user
    db: Session = Depends(get_db_session) # DB session
):
    # 1. Get the inventory item, ensure it belongs to the user
    item = db.query(Inventory).filter(
        Inventory.id == item_id,
        Inventory.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found or does not belong to user")

    if consumption_data.quantity <= 0:
         raise HTTPException(status_code=400, detail="Quantity must be positive")

    # Optional: Prevent consuming more than available, depending on how quantity is tracked
    # if consumption_data.quantity > item.quantity:
    #      raise HTTPException(status_code=400, detail=f"Cannot consume {consumption_data.quantity}, only {item.quantity} available")

    # 2. Calculate consumed nutrition
    consumed_calories = item.calories_per_serving * consumption_data.quantity
    consumed_protein = item.protein_g_per_serving * consumption_data.quantity
    consumed_carbs = item.carbs_g_per_serving * consumption_data.quantity
    consumed_fats = item.fats_g_per_serving * consumption_data.quantity

    # 3. Create a consumption log entry
    log_entry = ConsumptionLog(
        user_id=current_user.id,
        inventory_item_id=item.id, # Link to the item
        item_name_snapshot=item.name, # Snapshot name
        quantity_consumed=consumption_data.quantity,
        calories_consumed=consumed_calories,
        protein_consumed=consumed_protein,
        carbs_consumed=consumed_carbs,
        fats_consumed=consumed_fats,
        consumed_at=datetime.utcnow()
    )

    db.add(log_entry)

    # 4. Optional: Update inventory quantity (if you are tracking depletion there)
    # item.quantity -= consumption_data.quantity
    # if item.quantity < 0: item.quantity = 0 # Prevent negative quantity

    db.commit()
    db.refresh(log_entry)

    # 5. Return success response
    return {
        "consumption_log_id": log_entry.id,
        "consumed_quantity": log_entry.quantity_consumed,
        "calories": log_entry.calories_consumed,
        "protein_g": log_entry.protein_consumed,
        "carbs_g": log_entry.carbs_consumed,
        "fats_g": log_entry.fats_consumed
    }
```

```python
# 6.4 Daily Tracker Summary Example
# Assume DB models (ConsumptionLog, User) and DB session dependency exist
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date, time
from typing import Dict, Any

# Placeholder DB session dependency (replace with actual)
def get_db_session():
    # yield SessionLocal()
    pass # Replace with real session manager

# Placeholder function to calculate TDEE (should reuse logic from user profile)
def calculate_tdee(user: UserInDB) -> float:
    # Implement the BMR * activity factor calculation
    return 2000.0 # Mock value

# Endpoint
@app.get("/api/v1/tracker/daily")
async def get_daily_tracker(
    current_user: UserInDB = Depends(get_current_user), # Authenticated user
    db: Session = Depends(get_db_session) # DB session
) -> Dict[str, Any]: # Use Dict[str, Any] or a Pydantic model for response
    today_utc = datetime.utcnow().date()
    start_of_day_utc = datetime.combine(today_utc, time.min) # Or use timezones properly

    # 1. Calculate total consumed calories/macros for today
    daily_summary = db.query(
        func.sum(ConsumptionLog.calories_consumed).label("total_calories"),
        func.sum(ConsumptionLog.protein_consumed).label("total_protein"),
        func.sum(ConsumptionLog.carbs_consumed).label("total_carbs"),
        func.sum(ConsumptionLog.fats_consumed).label("total_fats")
    ).filter(
        ConsumptionLog.user_id == current_user.id,
        ConsumptionLog.consumed_at >= start_of_day_utc
    ).one_or_none() # Use one_or_none as aggregation always returns one row

    # Handle case where no consumption logs exist for today
    consumed_calories = daily_summary.total_calories if daily_summary and daily_summary.total_calories is not None else 0
    consumed_protein = daily_summary.total_protein if daily_summary and daily_summary.total_protein is not None else 0
    consumed_carbs = daily_summary.total_carbs if daily_summary and daily_summary.total_carbs is not None else 0
    consumed_fats = daily_summary.total_fats if daily_summary and daily_summary.total_fats is not None else 0


    # 2. Get inventory depletion log for today
    depletion_logs = db.query(
        ConsumptionLog.item_name_snapshot,
        ConsumptionLog.quantity_consumed,
        ConsumptionLog.consumed_at
    ).filter(
        ConsumptionLog.user_id == current_user.id,
        ConsumptionLog.consumed_at >= start_of_day_utc
    ).order_by(ConsumptionLog.consumed_at).all()

    # 3. Get user's target calories (TDEE)
    target_calories = calculate_tdee(current_user)

    # 4. Return the summary
    return {
        "date": today_utc.isoformat(),
        "target_calories": target_calories,
        "consumed_calories": consumed_calories,
        "consumed_protein_g": consumed_protein,
        "consumed_carbs_g": consumed_carbs,
        "consumed_fats_g": consumed_fats,
        "inventory_depletion_log": [
            {
                "item_name": log.item_name_snapshot,
                "quantity": log.quantity_consumed,
                "timestamp": log.consumed_at.isoformat() # Format timestamp
            } for log in depletion_logs
        ]
    }

```

```python
# 6.5 Recipe Generation with GEMINI API and Structured Output Example
# Assume necessary imports for DB models and LangChain integration
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.services.recipe_service import RecipeService # Our new service with structured output

# Placeholder DB session dependency (replace with actual)
def get_db_session():
    # yield SessionLocal()
    pass # Replace with real session manager

# Endpoint
@app.post("/api/v1/recipes/generate-from-inventory")
async def generate_recipe(
    current_user: UserInDB = Depends(get_current_user), # Authenticated user
    db: Session = Depends(get_db_session) # DB session
) -> Dict[str, Any]: # Return ingredients and instructions as lists of strings

    # Use our new service that integrates with GEMINI and uses structured output
    recipe_service = RecipeService()
    try:
        recipe_data = recipe_service.generate_recipe_from_inventory(db, current_user.id)
        return recipe_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}")

```
