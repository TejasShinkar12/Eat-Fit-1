```markdown
# Product Requirements Document: PantryFit MVP

**Version:** 1.0
**Date:** May 25, 2025

## 1. Document Header

**Product Name:** PantryFit (MVP)
**Document Version:** 1.0
**Date:** May 25, 2025
**Author:** [Your Name/Team]
**Status:** Draft

## 2. Executive Summary

PantryFit is a mobile-first (or web) application designed to help users track their food inventory, monitor nutritional intake based on fitness goals, and generate healthy recipes using available ingredients. The core innovation lies in automating food inventory logging by processing images of users' pantries or fridges using computer vision and OCR. This MVP focuses on providing essential functionality: user authentication, image-based inventory ingestion, manual inventory management, automated calorie and macronutrient tracking, basic recipe generation, and simple reporting.

## 3. Product Vision

The vision for PantryFit is to become the leading intelligent personal nutrition and inventory management companion. We aim to empower users to make healthier food choices, minimize food waste, and achieve their fitness goals by providing effortless tracking and personalized insights. By automating the tedious process of manual logging, PantryFit removes a significant barrier to consistent nutrition tracking. The long-term goal is to evolve into a comprehensive platform offering advanced meal planning, shopping list generation, community features, and deeper integration with health data, all powered by smart inventory management. Our target users are health-conscious individuals, busy families, and anyone looking to better manage their food resources and dietary habits.

## 4. User Personas

**Persona 1: Sarah - The Busy Professional**

*   **Background:** Sarah is 32, works long hours in a demanding job, and tries to maintain a healthy lifestyle but struggles with time. She often buys groceries with good intentions but forgets what she has or how long it's been there, leading to waste. She wants to eat healthier to manage stress and energy levels but finds manual calorie tracking tedious.
*   **Goals:**
    *   Quickly see what food she has available.
    *   Reduce food waste.
    *   Easily track her daily calorie and macro intake without manual logging.
    *   Find simple, healthy recipes she can make with ingredients she already owns.
*   **Pain Points:**
    *   Lack of time for detailed food logging.
    *   Forgetting about ingredients she has, leading to expiry.
    *   Struggling to plan meals efficiently.
    *   Feeling overwhelmed by complex nutrition apps.

**Persona 2: David - The Fitness Enthusiast**

*   **Background:** David is 25, actively works out, and is focused on precise macronutrient tracking to support his goal of gaining muscle mass. He's disciplined but finds logging *every* item manually time-consuming, especially when dealing with packaged foods with nutrition labels. He's curious about his consumption patterns over time.
*   **Goals:**
    *   Accurately track daily calories, protein, carbs, and fats.
    *   Easily log packaged foods without typing everything out.
    *   Monitor his nutrient intake trends over the week.
    *   Get alerts if his intake is significantly off his daily target.
*   **Pain Points:**
    *   Manual entry of nutrition info for every food item.
    *   Difficulty remembering expiry dates for supplements or specific ingredients.
    *   Lack of insight into which specific foods contribute most to certain nutrients.

## 5. Feature Specifications

### 5.1. Feature: User Authentication & Profile Setup

*   **Description:** Allows users to create an account, log in securely, and set up a basic profile containing key fitness metrics.
*   **User Stories:**
    *   As a new user, I want to sign up with my email and password so I can create an account.
    *   As a returning user, I want to log in with my email and password so I can access my data.
    *   As a user, I want to enter my height, weight, age, sex, activity level, and fitness goal so the app can calculate my nutritional needs.
    *   As a user, I want to be able to view and edit my profile details.
*   **Acceptance Criteria:**
    *   Users can successfully sign up with a unique email and a password meeting minimum complexity (e.g., > 6 characters).
    *   Users receive appropriate error messages for invalid sign-up attempts (e.g., email already exists, invalid format).
    *   Users can successfully log in with correct credentials.
    *   Users receive an error message for incorrect login credentials.
    *   The profile setup form collects height (units: cm/inches), weight (units: kg/lbs), age (years), sex (Male/Female), activity level (Low/Moderate/High - define simple criteria for each), and fitness goal (Gain/Lose/Maintain).
    *   All profile fields are required to proceed with profile setup.
    *   Users can navigate to a profile view showing their current details.
    *   Users can edit their profile details and save changes successfully.
*   **Edge Cases:**
    *   User enters non-numeric values for height, weight, or age.
    *   User enters values outside a reasonable range (e.g., age 0 or 200).
    *   User attempts to sign up with an email already in use.
    *   User forgets password (out of scope for MVP password reset functionality).

### 5.2. Feature: Inventory Ingestion via Image

*   **Description:** Enables users to upload a photo of their food items (packaged goods) to automatically populate their inventory.
*   **User Stories:**
    *   As a user, I want to upload a photo of items in my pantry/fridge so the app can automatically add them to my inventory.
    *   As a user, I want the app to identify packaged food items and read their nutrition labels.
    *   As a user, I want the extracted information (item name, calories, macros, expiry) to be saved to my inventory.
*   **Acceptance Criteria:**
    *   The application provides an interface for users to upload an image (or take a photo if on mobile).
    *   The uploaded image is processed by the specified pipeline (Object Detection + OCR).
    *   For each detected packaged food item, the pipeline attempts to extract: Item Name, Calories per Serving, Protein per Serving, Carbs per Serving, Fats per Serving, and Expiry Date (if clearly visible and in a standard format).
    *   Extracted data for *at least one* item in the photo is successfully saved to the user's inventory in PostgreSQL.
    *   Quantity defaults to 1 for newly ingested items via image.
    *   The system handles cases where detection/OCR fails partially or completely for an item (e.g., logs item name if possible, leaves nutrition fields blank).
    *   Users are notified whether the ingestion was successful and how many items were added/updated.
*   **Edge Cases:**
    *   Poor image quality (blurry, poor lighting, angled).
    *   Items are obscured or overlapping.
    *   Nutrition labels are damaged, non-standard, or not in English.
    *   Multiple identical items in the photo (MVP defaults quantity to 1 per detection, not summing identical items).
    *   Non-packaged food items in the photo (ignored).
    *   Expiry dates in non-standard formats or unclear fonts.
    *   Pipeline takes too long to process (MVP may have simple loading state, no advanced async processing).
    *   Zero items detected in the image.

### 5.3. Feature: Inventory View & Manual Edits

*   **Description:** Allows users to view their current inventory, manually add new items, edit existing item details, delete items, and mark items as consumed.
*   **User Stories:**
    *   As a user, I want to see a list of all food items in my inventory.
    *   As a user, I want to see the name, nutritional info, and expiry date for each item.
    *   As a user, I want to manually add a new food item to my inventory.
    *   As a user, I want to edit the details (name, quantity, nutrition, expiry) of an item in my inventory.
    *   As a user, I want to delete an item from my inventory.
    *   As a user, I want to mark a specific quantity of an item as consumed so it's tracked for my daily intake.
*   **Acceptance Criteria:**
    *   Users can access a dedicated "Inventory" screen listing all items currently in their database.
    *   Each listed item displays its Name, Quantity, Calories per Serving, and Expiry Date.
    *   A clear button/interface allows users to add a new item manually.
    *   Manual add form allows input for Item Name, Quantity, Calories/Serving, Protein/Serving, Carbs/Serving, Fats/Serving, and optional Expiry Date.
    *   Added manual items appear in the inventory list.
    *   Users can click/select an item to view or edit its full details.
    *   Users can successfully edit item details (including quantity) and save changes.
    *   Users can successfully delete an item from the list.
    *   For each item, there is an action (e.g., button, swipe) to "Mark as Consumed".
    *   Marking as consumed prompts the user to specify the quantity consumed (e.g., number of servings).
    *   Marking an item as consumed with a specific quantity creates a corresponding entry in the `consumption_log` table (timestamp, user_id, item_id, quantity_consumed).
    *   Marking an item as consumed does *not* automatically reduce its quantity in the `inventory` table in the MVP (Inventory depletion log handles this visually/conceptually, actual quantity management is manual edit for MVP simplicity). *Self-correction: Let's make it update quantity for MVP, that's more useful. Marking consumed *does* reduce inventory quantity.*
*   **Edge Cases:**
    *   Entering non-numeric data for quantities or nutrition fields during manual add/edit.
    *   Entering an expiry date in the past.
    *   Marking consumed quantity greater than available quantity (allow, but maybe flag in future versions; MVP just logs the consumption). *Self-correction: Let's require consumed quantity <= current inventory quantity for simplicity in MVP.*
    *   Attempting to delete an item that was previously consumed (MVP allows deletion, consumption log entry remains).
    *   Empty inventory list.

### 5.4. Feature: Fitness Profile-Based Calorie Tracking

*   **Description:** Calculates user's daily target calories/macros and tracks consumption based on items marked as consumed from the inventory.
*   **User Stories:**
    *   As a user, I want to see my estimated daily calorie and macronutrient needs based on my profile.
    *   As a user, I want to see how many calories and macros I have consumed today.
    *   As a user, I want to see a dashboard summarizing my daily intake compared to my target.
*   **Acceptance Criteria:**
    *   Upon profile setup completion, the application calculates the user's Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE). Use a standard formula like Mifflin-St Jeor for BMR and standard activity multipliers for TDEE.
    *   Fitness goal adjusts TDEE target (e.g., +500 kcal for gain, -500 kcal for lose; Maintain is TDEE).
    *   A "Today's Consumption" view or dashboard is available.
    *   This view displays the user's target daily calories and macronutrients (Protein, Carbs, Fats).
    *   The view displays the total calories, protein, carbs, and fats consumed *today* based on summing up entries in the `consumption_log` for the current user from midnight.
    *   Consumption calculation uses the nutrition info stored *with the item at the time of consumption* (or latest available if design simplifies this) multiplied by the quantity consumed.
    *   A visual indicator (e.g., progress bar, simple number comparison) shows calories consumed vs. target.
    *   Macronutrient breakdown (Protein, Carbs, Fats) is displayed, perhaps as percentages or grams.
*   **Edge Cases:**
    *   User has not completed profile setup (tracking dashboard not available or shows guidance).
    *   User has no consumption log entries for the day (consumed numbers show 0).
    *   Edge cases in BMR/TDEE calculation formula results (use standard formulas, no need for complex validation on output ranges for MVP).

### 5.5. Feature: Recipe Generator

*   **Description:** Generates simple recipes using the items currently available in the user's inventory, tailored loosely to their fitness goal.
*   **User Stories:**
    *   As a user, I want to generate a recipe using items I currently have in my inventory.
    *   As a user, I want the recipe suggestions to consider my fitness goal (gain/lose/maintain).
    *   As a user, I want to see the ingredients and instructions for the generated recipe.
*   **Acceptance Criteria:**
    *   The feature queries the user's current inventory items (based on quantity > 0).
    *   It uses a text-to-text model (e.g., flan-t5) with a prompt incorporating the list of *available* inventory items and the user's fitness goal.
    *   The model generates a recipe suggestion including a list of ingredients and simple instructions in text format.
    *   The generated recipe is displayed to the user.
    *   The system handles cases where the model fails to generate a coherent recipe or a recipe using *only* the provided items (display a "Could not generate recipe" message).
    *   Recipes are generated on demand and are not necessarily saved (saving is optional per data model).
*   **Edge Cases:**
    *   Empty inventory (no items to generate a recipe from).
    *   Inventory contains only items that don't typically form a meal (e.g., just spices, condiments).
    *   Model generates a recipe requiring items *not* in the inventory (MVP shows the output as is, no strict validation).
    *   Model generates a nonsensical or unsafe recipe (rely on model capability, no complex safety checks for MVP).
    *   Latency in model response.

### 5.6. Feature: Reports & Alerts

*   **Description:** Provides basic visual reports on nutrient trends and triggers alerts for calorie goals and item expiry.
*   **User Stories:**
    *   As a user, I want to see how my calorie and macronutrient intake has trended over the past week.
    *   As a user, I want to see which specific food items contributed most to a certain nutrient (e.g., sugar, fat) over a period.
    *   As a user, I want to be alerted if my daily calorie intake is significantly above or below my target.
    *   As a user, I want to be alerted when an item in my inventory is about to expire.
*   **Acceptance Criteria:**
    *   A "Reports" section is accessible.
    *   It displays a visual representation (e.g., simple bar or line chart) showing daily calorie intake for the past 7 days.
    *   It displays a breakdown (e.g., pie chart or simple list) of total protein, carbs, and fats consumed over the past 7 days.
    *   It identifies and lists the top 3-5 food items contributing the most to total calories, protein, carbs, *or* fats over the past 7 days based on consumption logs.
    *   The system triggers an alert (e.g., in-app notification, simple indicator on dashboard) if the user's *today's* calorie consumption deviates by more than a defined percentage (e.g., +/- 20%) from their daily target TDEE.
    *   The system triggers an alert (e.g., in-app notification, indicator on inventory list) for any item in the inventory with an expiry date within the next 2 days.
*   **Edge Cases:**
    *   Less than 7 days of consumption data available (charts show data only for available days).
    *   No consumption data at all (reports are empty, alerts aren't triggered).
    *   No items with expiry dates, or no items expiring within 2 days (no expiry alerts).
    *   User manually enters items/nutrition without marking them consumed (they won't appear in consumption-based reports/alerts).

### 5.7. Feature: Basic Voice & Text Q&A (Optional for MVP)

*   **Description:** (Optional for MVP) Allows users to ask simple questions about their inventory and consumption using text input.
*   **User Stories:**
    *   As a user, I want to ask a text question like "What's in my fridge?" and get a list of my current inventory.
    *   As a user, I want to ask a text question like "How much protein did I consume today?" and get a numerical answer.
*   **Acceptance Criteria:**
    *   (If implemented for MVP) A text input field is available for questions.
    *   System recognizes simple questions related to "what's in inventory" and "today's macro/calorie consumption".
    *   Provides relevant, text-based answers querying the database.
*   **Edge Cases:**
    *   User asks a question outside the recognized scope.
    *   Question is ambiguous or poorly phrased.
    *   No data available to answer the question.
    *   (Voice input via Whisper is explicitly optional for MVP).

## 6. Technical Requirements

*   **Backend:**
    *   Framework: FastAPI (Python) for building RESTful APIs.
    *   Database: PostgreSQL for persistent storage of user data, inventory, and consumption logs.
    *   ML/AI Models (Hugging Face):
        *   Object Detection: A fine-tuned Detectron2-based model (or similar capable HF model) for identifying packaged food items in images.
        *   OCR: TrOCR or a similar Transformer-based OCR model for extracting text from nutrition labels and expiry dates.
        *   Text Generation: Flan-T5 or a similar Text2Text Transformer model for recipe generation.
        *   Speech-to-Text: Whisper (Optional for MVP voice input).
    *   Data Processing: Python libraries (e.g., OpenCV, Pillow, PyTorch/TensorFlow, Transformers) for image processing and ML model inference.
    *   Authentication: Secure password hashing (e.g., bcrypt) and token-based authentication (e.g., JWT).
*   **Frontend:**
    *   Framework: React or React Native (depending on mobile vs. web focus). Communicates with the FastAPI backend via REST API calls. Handles user interface, data display, form inputs, and image uploads.
*   **Data Storage (PostgreSQL Schema):**
    *   `users` table:
        *   `id` (UUID/Integer, Primary Key)
        *   `email` (Text, Unique, Not Null)
        *   `password_hash` (Text, Not Null)
        *   `created_at` (Timestamp, Default Now)
        *   `updated_at` (Timestamp, Default Now)
        *   `height_cm` (Numeric)
        *   `weight_kg` (Numeric)
        *   `age_years` (Integer)
        *   `sex` (Text - e.g., 'Male', 'Female')
        *   `activity_level` (Text - e.g., 'Low', 'Moderate', 'High')
        *   `fitness_goal` (Text - e.g., 'Gain', 'Lose', 'Maintain')
        *   `bmr` (Numeric, Calculated)
        *   `tdee` (Numeric, Calculated)
        *   `target_calories` (Numeric, Calculated based on TDEE and goal)
        *   `target_protein_g` (Numeric, Calculated based on TDEE/Goal)
        *   `target_carbs_g` (Numeric, Calculated based on TDEE/Goal)
        *   `target_fats_g` (Numeric, Calculated based on TDEE/Goal)
    *   `inventory` table:
        *   `id` (UUID/Integer, Primary Key)
        *   `user_id` (UUID/Integer, Foreign Key to users.id, Not Null)
        *   `name` (Text, Not Null)
        *   `quantity` (Numeric, Default 1.0, Not Null)
        *   `calories_per_serving` (Numeric, Nullable)
        *   `protein_g_per_serving` (Numeric, Nullable)
        *   `carbs_g_per_serving` (Numeric, Nullable)
        *   `fats_g_per_serving` (Numeric, Nullable)
        *   `serving_size_unit` (Text, Optional - e.g., 'g', 'ml', 'item')
        *   `expiry_date` (Date, Nullable)
        *   `added_at` (Timestamp, Default Now)
        *   `updated_at` (Timestamp, Default Now)
        *   `source` (Text - e.g., 'image', 'manual')
    *   `consumption_log` table:
        *   `id` (UUID/Integer, Primary Key)
        *   `user_id` (UUID/Integer, Foreign Key to users.id, Not Null)
        *   `inventory_item_id` (UUID/Integer, Foreign Key to inventory.id, Nullable - in case of manual consumption not linked to inventory)
        *   `item_name` (Text, Not Null - Store name directly for easier logging/reporting if inventory item is deleted)
        *   `quantity_consumed` (Numeric, Not Null)
        *   `calories_consumed` (Numeric, Not Null - Calculated at time of consumption)
        *   `protein_consumed_g` (Numeric, Not Null)
        *   `carbs_consumed_g` (Numeric, Not Null)
        *   `fats_consumed_g` (Numeric, Not Null)
        *   `consumed_at` (Timestamp, Default Now, Not Null)
    *   `recipes` table (Optional for MVP persistence):
        *   `id` (UUID/Integer, Primary Key)
        *   `user_id` (UUID/Integer, Foreign Key to users.id, Not Null)
        *   `generated_at` (Timestamp, Default Now)
        *   `prompt_items` (Text Array or JSONB - List of items used in prompt)
        *   `fitness_goal` (Text)
        *   `recipe_text` (Text - The generated recipe content)
    *   Redis (Optional): For caching frequently accessed data (e.g., user profile calculations, recent consumption summaries) or potentially rate-limiting API calls. Not strictly required for MVP functionality but good for performance planning.
*   **Deployment:** Must be deployable on a cloud platform (Render, Heroku, AWS, GCP, Azure). This requires containerization (Docker) and appropriate configuration for database connections and ML model serving/access.

## 7. Implementation Roadmap

This roadmap outlines a possible sequence for implementing the MVP features, prioritizing foundational elements and core value propositions.

**Phase 1: Foundation & Manual Core (Approx. 2-3 Weeks)**

*   **Feature 1: User Authentication & Profile Setup**
    *   Implement database schema for `users`.
    *   Build sign-up and login API endpoints.
    *   Develop frontend screens for sign-up, login, and basic dashboard shell.
    *   Implement password hashing and basic authentication.
    *   Build profile setup form and API endpoint to save data to `users` table.
    *   Implement profile view/edit functionality.
*   **Feature 3 (Part 1): Inventory View & Manual Edits (Add/View/Delete)**
    *   Implement database schema for `inventory`.
    *   Build API endpoints for adding, viewing (listing/detail), and deleting inventory items manually.
    *   Develop frontend screens/components for inventory list view, manual add form, and item detail/delete action.

**Phase 2: Core Automation & Tracking (Approx. 3-4 Weeks)**

*   **Feature 2: Inventory Ingestion via Image**
    *   Integrate selected Object Detection and OCR models (Hugging Face APIs or self-hosted).
    *   Build FastAPI endpoint to receive image uploads.
    *   Implement the image processing pipeline logic (detection, OCR, data extraction).
    *   Implement saving extracted data to the `inventory` table.
    *   Develop frontend component for image upload and displaying processing results/status.
*   **Feature 4: Fitness Profile-Based Calorie Tracking**
    *   Refine `users` table schema to include calculated BMR, TDEE, and target macros.
    *   Implement calculation logic for BMR/TDEE/Targets upon profile setup/update.
    *   Implement database schema for `consumption_log`.
    *   Build API endpoint to log consumption based on quantity and item ID.
    *   Update Feature 3 frontend to include "Mark as Consumed" action which calls the consumption log API.
    *   Develop API endpoint to retrieve daily consumption data (calories, macros).
    *   Develop frontend dashboard components to display TDEE target, consumed calories/macros.

**Phase 3: Value-Add & Insights (Approx. 2-3 Weeks)**

*   **Feature 5: Recipe Generator**
    *   Integrate selected Text2Text model (Hugging Face API or self-hosted).
    *   Build API endpoint that queries available inventory, constructs the prompt, calls the text generation model.
    *   Develop frontend component to trigger recipe generation and display the text output. (Optional: Add `recipes` table if saving generated recipes is desired for MVP).
*   **Feature 6: Reports & Alerts**
    *   Build API endpoints to query consumption data for weekly trends and top contributors.
    *   Implement logic for identifying top contributors.
    *   Develop frontend components to display simple charts (e.g., using a charting library) for weekly trends.
    *   Develop backend logic and API endpoints for checking daily calorie target deviation and item expiry dates.
    *   Implement basic in-app notification/alert display on the frontend (e.g., dashboard indicator, inventory list highlight).

**Phase 4: Polish & Deployment (Approx. 1 Week)**

*   Refine UI/UX based on initial testing.
*   Implement basic input validation and error handling across all features.
*   Write unit and integration tests.
*   Set up deployment pipeline and deploy to chosen cloud provider (Render/Heroku).
*   Perform end-to-end testing on the deployed environment.
*   Ensure MVP success criteria are met.

**Post-MVP (Future Considerations):**

*   Feature 7: Basic Voice & Text Q&A (Integrate Whisper, enhance text querying).
*   Admin Tools: CSV export, Debugging interfaces.
*   Advanced Features: Barcode scanning, meal planning, shopping list generation, community features, integration with wearables, refined ML models.

---
```
