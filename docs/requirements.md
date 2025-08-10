```markdown
# Project Requirements Document

**Project Name:** (e.g., FridgeFit) - An AI-Powered Inventory & Nutrition Tracker
**Version:** 1.0
**Date:** May 25, 2025

---

## 1. Document Header

```markdown
# Project Requirements Document

**Project Name:** (e.g., FridgeFit) - An AI-Powered Inventory & Nutrition Tracker
**Version:** 1.0
**Date:** May 25, 2025
```

---

## 2. Project Overview

**Purpose:**
The primary purpose of this project is to develop a minimum viable product (MVP) for a food inventory and nutrition tracking application. The application leverages computer vision (Object Detection, OCR) to automate the initial input of pantry/fridge contents and nutrition information, integrating this data with user-defined fitness goals for automated calorie and macronutrient tracking.

**Goals:**
*   Enable users to easily add their food inventory through image uploads.
*   Automatically extract key nutrition data from food packaging labels.
*   Provide a clear view and manual editing capabilities for the food inventory.
*   Calculate and track daily calorie and macronutrient intake based on consumed items and user profile.
*   Generate simple recipe suggestions based on available inventory.
*   Provide basic reports and alerts related to nutrition trends and inventory expiry.

**Target Users:**
Individuals who are health-conscious, tracking their fitness goals (weight gain/loss/maintenance), interested in understanding their food consumption, and looking for a more automated way to manage their kitchen inventory and nutrition tracking compared to purely manual logging.

---

## 3. Functional Requirements

This section details the core features of the MVP and their acceptance criteria.

### FR 1: User Authentication & Profile Setup

*   **FR 1.1 - User Registration:**
    *   **Description:** Allow new users to create an account using their email address and a password.
    *   **Acceptance Criteria:**
        *   User can successfully sign up with a unique email address.
        *   System stores the email and a hashed password securely.
        *   User receives confirmation of successful registration (e.g., via UI message).
*   **FR 1.2 - User Login:**
    *   **Description:** Allow registered users to log into their account.
    *   **Acceptance Criteria:**
        *   Registered user can log in successfully using their registered email and correct password.
        *   Login attempt fails if the email is not registered or the password is incorrect.
        *   Authenticated session is established upon successful login.
*   **FR 1.3 - Fitness Profile Setup:**
    *   **Description:** Capture essential user fitness profile data required for calculating nutritional needs.
    *   **Acceptance Criteria:**
        *   User can input height (units selectable or specified, e.g., cm/inches), weight (units selectable, e.g., kg/lbs), age, sex (Male/Female/Other), activity level (e.g., Low, Moderate, High).
        *   User can select a primary fitness goal (Gain Weight, Lose Weight, Maintain Weight).
        *   All profile data is stored and associated with the user's account.

### FR 2: Inventory Ingestion via Image

*   **FR 2.1 - Image Upload:**
    *   **Description:** Allow users to upload a photo of their pantry or fridge contents.
    *   **Acceptance Criteria:**
        *   User can select an image file from their device and upload it through the application interface.
        *   The system receives the image file for processing.
*   **FR 2.2 - Object Detection Pipeline:**
    *   **Description:** Process the uploaded image using an object detection model to identify packaged food items.
    *   **Acceptance Criteria:**
        *   The backend processing pipeline is triggered upon image upload.
        *   The model attempts to identify distinct food items within the image.
        *   Potential bounding boxes or regions of interest for identified items are generated internally.
*   **FR 2.3 - OCR Pipeline (Nutrition Labels):**
    *   **Description:** Apply OCR technology to the identified items or relevant label regions to extract key nutrition information.
    *   **Acceptance Criteria:**
        *   For detected items with visible text labels, the system attempts to extract values for Calories, Protein, Carbohydrates (Carbs), and Fats.
        *   Extracted data fields are parsed and prepared for storage.
        *   *Note:* Accuracy is subject to image quality and model performance; manual edits are expected.
*   **FR 2.4 - Data Consolidation and Storage:**
    *   **Description:** Combine the results from detection and OCR, adding default/estimated values, and save the item data to the user's inventory.
    *   **Acceptance Criteria:**
        *   For each successfully processed item, the system attempts to determine an "Item Name" (may require model or external lookup, or be a generic label).
        *   Quantity is defaulted to 1 unless specified otherwise (MVP defaults to 1).
        *   Extracted Calories, Protein, Carbs, and Fats per serving are associated with the item.
        *   Expiry date is extracted if clearly visible on the label (optional capture for MVP, prioritize core nutrition).
        *   The structured data for each processed item is stored in the `inventory` table linked to the user ID.
        *   *Note:* The system should handle cases where detection or OCR fails for specific items (e.g., requiring manual addition).

### FR 3: Inventory View & Manual Edits

*   **FR 3.1 - Inventory Listing:**
    *   **Description:** Display a list of all items currently in the user's inventory.
    *   **Acceptance Criteria:**
        *   User can navigate to an Inventory screen.
        *   The screen shows a list of items, including their name, a summary of nutrition information (e.g., Calories, Protein), and expiry date (if available).
*   **FR 3.2 - Manual Item Add:**
    *   **Description:** Allow users to manually add items to their inventory if image ingestion is incomplete or fails.
    *   **Acceptance Criteria:**
        *   User can initiate adding a new item manually.
        *   User can input Item Name, Quantity, Calories per serving, Protein per serving, Carbs per serving, Fats per serving, and Expiry Date (optional).
        *   The manually added item appears in the inventory list.
*   **FR 3.3 - Manual Item Edit:**
    *   **Description:** Allow users to modify the details of existing inventory items.
    *   **Acceptance Criteria:**
        *   User can select an item from the inventory list for editing.
        *   User can modify any field (Name, Quantity, Nutrition values, Expiry).
        *   Changes are saved and reflected in the inventory list.
*   **FR 3.4 - Manual Item Delete:**
    *   **Description:** Allow users to remove items from their inventory.
    *   **Acceptance Criteria:**
        *   User can select an item from the inventory list and choose to delete it.
        *   The item is removed from the inventory list.
*   **FR 3.5 - Mark Item as Consumed:**
    *   **Description:** Allow users to indicate that they have consumed a portion of an inventory item, updating their daily calorie tracker.
    *   **Acceptance Criteria:**
        *   User can select an inventory item and mark a specified number of servings as consumed.
        *   The system reduces the quantity of the item in the inventory (if quantity tracking is implemented beyond '1' or if marking the 'last' serving).
        *   A record of the consumption (item, servings, nutrition data, timestamp) is added to the `consumption_log` table.
        *   The nutrition data for the consumed servings contributes to the daily consumption totals tracked in FR 4.

### FR 4: Fitness Profile-Based Calorie Tracking

*   **FR 4.1 - TDEE Calculation:**
    *   **Description:** Calculate the user's estimated Total Daily Energy Expenditure (TDEE) based on their fitness profile (FR 1.3).
    *   **Acceptance Criteria:**
        *   The system calculates the user's Basal Metabolic Rate (BMR) using a standard formula (e.g., Mifflin-St Jeor or Harris-Benedict, specify which or allow flexibility).
        *   The system calculates TDEE by multiplying BMR by an activity level multiplier.
        *   The system determines a daily calorie target based on the TDEE and the user's fitness goal (e.g., TDEE +/- calorie deficit/surplus for weight change goals).
*   **FR 4.2 - Daily Consumption Aggregation:**
    *   **Description:** Aggregate the nutritional data (Calories, Protein, Carbs, Fats) from all items marked as consumed on the current day.
    *   **Acceptance Criteria:**
        *   The system retrieves all `consumption_log` entries for the current 24-hour period for the user.
        *   Total Calories, Protein (g), Carbs (g), and Fats (g) are summed from these entries.
*   **FR 4.3 - Dashboard Display (Calories):**
    *   **Description:** Show the user's daily calorie consumption compared to their calculated target on a dashboard or summary screen.
    *   **Acceptance Criteria:**
        *   A dashboard element displays the "Total Calories Consumed Today" and the "Daily Calorie Target".
        *   Visual representation (e.g., progress bar) is optional but helpful for clarity.
*   **FR 4.4 - Dashboard Display (Macronutrients):**
    *   **Description:** Show the user's daily consumption breakdown by macronutrient (Protein, Carbs, Fats) on the dashboard.
    *   **Acceptance Criteria:**
        *   A dashboard element displays the total grams of Protein, Carbohydrates, and Fats consumed today.
*   **FR 4.5 - Inventory Depletion Log:**
    *   **Description:** Show a log of items the user has marked as consumed.
    *   **Acceptance Criteria:**
        *   User can access a screen or section showing a chronological list of consumed items (item name, quantity/servings, timestamp, maybe nutrition summary).

### FR 5: Recipe Generator

*   **FR 5.1 - Inventory Query for Recipe Generation:**
    *   **Description:** Prepare the user's current inventory list as input for the recipe generation model.
    *   **Acceptance Criteria:**
        *   Upon user request for a recipe, the system retrieves the list of items currently in the user's inventory.
*   **FR 5.2 - Recipe Generation via LLM:**
    *   **Description:** Use a Text2Text model to generate a recipe based on available inventory items and the user's fitness goal.
    *   **Acceptance Criteria:**
        *   The system constructs a prompt for the language model including the inventory list and the user's weight goal (gain/lose/maintain).
        *   The model processes the prompt and generates text output intended to be a recipe.
        *   *Note:* Recipe quality is subject to model capabilities and prompt engineering; generated recipes might be basic or require manual interpretation.
*   **FR 5.3 - Recipe Display:**
    *   **Description:** Present the generated recipe (ingredients and instructions) to the user.
    *   **Acceptance Criteria:**
        *   The raw text output from the language model is displayed to the user on a dedicated screen or section.
        *   The display is simple text format.

### FR 6: Reports & Alerts

*   **FR 6.1 - Weekly Nutrient Trend Report:**
    *   **Description:** Show a visualization (chart) of calorie and/or macronutrient consumption trends over the past week.
    *   **Acceptance Criteria:**
        *   User can view a report showing daily totals for Calories and potentially Protein, Carbs, Fats for the last 7 days.
        *   The data is presented in a graphical format (e.g., bar chart for daily totals, pie chart for weekly macro breakdown - choose one type for MVP).
*   **FR 6.2 - Top Contributors Report:**
    *   **Description:** Identify and list items that have contributed the most to selected nutritional categories based on consumption.
    *   **Acceptance Criteria:**
        *   User can view a report showing which consumed items contributed the highest amounts to specific nutrients (e.g., "Top 3 items by Sugar," "Item with most Protein"). Focus on 1-2 nutrient types for MVP (e.g., total calories, protein).
*   **FR 6.3 - Calorie Intake Alert:**
    *   **Description:** Notify the user if their daily calorie intake deviates significantly from their target.
    *   **Acceptance Criteria:**
        *   The system checks daily consumption against the target.
        *   An alert message is generated if consumption is outside a predefined range (e.g., < 80% or > 120% of target).
        *   The alert is visible to the user (e.g., on dashboard or notification area - UI decision).
*   **FR 6.4 - Expiry Alert:**
    *   **Description:** Notify the user when an inventory item is approaching its expiry date.
    *   **Acceptance Criteria:**
        *   The system checks inventory items with expiry dates.
        *   An alert message is generated for items expiring within the next 2 days.
        *   The alert is visible to the user.

### FR 7: Basic Voice & Text Q&A (Text-Only for MVP)

*   **FR 7.1 - Text-based Inventory Query:**
    *   **Description:** Allow users to type simple questions about their inventory.
    *   **Acceptance Criteria:**
        *   User can type questions like "What's in my fridge?" or "What food do I have?".
        *   The system processes the text query (basic keyword matching for MVP is acceptable).
        *   The system responds with a text list of the user's current inventory items.
*   **FR 7.2 - Text-based Consumption Query:**
    *   **Description:** Allow users to type simple questions about their daily consumption.
    *   **Acceptance Criteria:**
        *   User can type questions like "How much protein did I consume today?".
        *   The system processes the text query (basic keyword matching).
        *   The system responds with a text summary of the requested nutrient consumed today (e.g., "You have consumed X grams of protein today.").

---

## 4. Non-Functional Requirements

*   **Performance:**
    *   Image processing pipeline (Object Detection & OCR) may take significant time (e.g., 1-5 minutes depending on image complexity, model size, processing power). User should be notified the process is running.
    *   Inventory viewing and manual editing should be responsive (load time < 2-3 seconds, update time < 1 second).
    *   Calorie/Macro tracking dashboard should load within 2-3 seconds.
    *   Recipe generation may take time depending on LLM performance (e.g., 10-30 seconds).
    *   Report generation should complete within 5 seconds.
*   **Security:**
    *   User passwords must be stored securely using industry-standard hashing algorithms.
    *   Data transmission between frontend and backend must be encrypted (HTTPS).
    *   Access to user data (profile, inventory, consumption) must be restricted to the authenticated user.
    *   Input validation should be implemented to prevent common vulnerabilities (e.g., SQL injection).
*   **Technical:**
    *   Adherence to the specified tech stack: FastAPI (Backend API), PostgreSQL (Database), Computer Vision models (trocr, detectron2-based) for image processing, GEMINI API via LangChain for recipe generation. Frontend using React (Web) or React Native (Mobile).
    *   The application must be deployable on standard cloud platforms (e.g., Render, Heroku, AWS, GCP).
    *   Codebase should be reasonably structured and commented for maintainability.
    *   API endpoints should be well-defined.

---

## 5. Dependencies and Constraints

*   **Dependencies:**
    *   Access to and integration with Hugging Face models/APIs for computer vision and natural language processing. Model availability and API stability are external dependencies.
    *   Availability of a PostgreSQL database instance.
    *   Required Python libraries (FastAPI, relevant ML/CV libraries, database drivers) and JavaScript/React libraries.
    *   Cloud hosting environment for deployment.
*   **Constraints:**
    *   **MVP Scope:** Development is strictly limited to the features defined in Section 3. Features marked 'Optional for MVP' are excluded unless scope changes.
    *   **Image Quality:** Accuracy of image processing (detection, OCR) is highly dependent on the quality, lighting, angle, and clarity of the uploaded images and food labels. Performance will vary significantly.
    *   **AI Model Accuracy:** The output quality of AI models (detection, OCR, recipe generation) is probabilistic and not 100% accurate. Manual correction features are critical to compensate for this.
    *   **Serving Sizes:** The system relies on nutrition information being "per serving". Users will need to indicate servings consumed. The system does not automatically detect serving sizes from images.
    *   **Recipe Relevance:** Generated recipes may not always be practical, desirable, or utilize all available ingredients due to LLM limitations.

---

## 6. Risk Assessment

*   **Risk 1: Low Accuracy of Image Processing (Detection & OCR)**
    *   **Description:** The core automation feature might fail frequently or produce inaccurate results (missed items, incorrect nutrition values) due to image quality, label variations, or model limitations.
    *   **Impact:** High (undermines primary value proposition, leads to user frustration, inaccurate tracking).
    *   **Likelihood:** High (CV on real-world pantry/fridge images is challenging).
    *   **Mitigation:** Prioritize robust manual editing features (FR 3.2, 3.3). Provide clear guidance on taking good photos. Manage user expectations regarding automation accuracy. Continuously monitor and potentially improve models post-MVP.
*   **Risk 2: Poor Performance of AI Models**
    *   **Description:** The processing time for image analysis or recipe generation could be excessively slow, leading to a poor user experience.
    *   **Impact:** Medium-High (delays user workflows, perceived as sluggish).
    *   **Likelihood:** Medium (depends on model size, server specs, and number of items).
    *   **Mitigation:** Implement asynchronous processing for image uploads. Provide progress indicators. Optimize model serving (e.g., batch processing, using GPUs if feasible). Manage user expectations regarding processing time.
*   **Risk 3: Data Inaccuracy (Cumulative)**
    *   **Description:** A combination of AI errors (Risk 1) and potential user errors during manual input/consumption logging could lead to inaccurate inventory, consumption logs, and subsequent reports/alerts.
    *   **Impact:** High (users rely on data for fitness goals; inaccurate data is misleading).
    *   **Likelihood:** High (multiple points of potential error).
    *   **Mitigation:** Make manual editing easy and prominent. Implement basic data validation where possible (e.g., ensure calorie values are numbers). Clearly label data source if possible (automated vs. manual). Encourage users to verify data.
*   **Risk 4: Integration Complexity with Hugging Face/External Services**
    *   **Description:** Integrating disparate AI models and managing their APIs/libraries within the backend framework could be technically challenging or encounter version conflicts.
    *   **Impact:** Medium (delays development, potential instability).
    *   **Likelihood:** Medium.
    *   **Mitigation:** Thoroughly test integrations early in development. Use dependency management tools effectively. Start with basic integration proof-of-concepts.
*   **Risk 5: Adoption Barriers**
    *   **Description:** Users might find the process of taking photos, uploading, and manually correcting items too cumbersome compared to traditional manual logging or alternative methods.
    *   **Impact:** High (low user engagement, project failure).
    *   **Likelihood:** Medium (depends heavily on UI/UX).
    *   **Mitigation:** Focus on a smooth and intuitive user interface (UI) and user experience (UX). Clearly communicate the benefits (e.g., "Scan once, track consumption easily"). Get user feedback early in development.

---
```
