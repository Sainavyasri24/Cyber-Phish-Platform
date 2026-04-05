# 🛡️ Cyber-Phish Platform: Complete Project Breakdown

Welcome to the **Cyber-Phish Platform**. If you are completely new to this project, this document will explain exactly what it is, why it exists, how it works, and every piece of technology used to build it. We will go through the project "pin-to-pin" so that anyone can understand the architecture from top to bottom.

---

## 1. What is this project?

The **Cyber-Phish Platform** acts as a **Secure Web Gateway (SWG)**. In simple terms, it is an intelligent security shield. 

When a user tries to visit a website (a URL), the most common way hackers steal passwords or money is by creating "Phishing" websites—sites that look legitimate (like a fake PayPal or Apple login) but are actually traps. 

Standard antivirus tools usually rely on "blocklists" (lists of known bad websites). The problem? Hackers create thousands of new websites every day. By the time a site is added to a blocklist, it's too late. 

**This project solves that problem using Artificial Intelligence.** Instead of just checking a list, our platform acts like a detective. It uses Machine Learning to deeply analyze the URL's patterns, network properties, and behaviors to predict if a link is dangerous—even if that link was created 5 minutes ago.

---

## 2. How the Platform Works (The Step-by-Step Flow)

Imagine a user logs into our platform and wants to check a link: `http://login-update-paypal-912.xyz/secure.php`. Here is exactly what happens behind the scenes:

1. **The User Interface (Frontend):** The user pastes the link into a clean, modern web application and clicks "Scan". 
2. **The API Request:** The web application packages that URL and sends it to our Backend Brain (API) securely over the network.
3. **Feature Extraction (The Investigation):** Before making a guess, the backend breaks the URL apart like a puzzle. It looks for clues (features):
   - *Is the URL unusually long?*
   - *Does it contain suspicious words like "login", "update", or "secure"?*
   - *Is the domain extension a high-risk one like `.xyz` or `.tk`?*
   - *How old is this website? (A 10-year-old site is usually safe; a site registered today is very suspicious).*
4. **The Machine Learning Brain:** The backend takes all these clues (usually 12 distinct measurements) and feeds them into our trained Artificial Intelligence model—specifically, a **Random Forest Classifier**.
5. **The Verdict:** The AI model processes the clues based on thousands of past examples it has studied and spits out a probability score (e.g., *99% chance this is a threat*).
6. **The Response:** The system categorizes the threat (Low, Medium, High Risk) and decides on an action:
   - **Low Risk:** Access Allowed.
   - **High Risk:** Blocked automatically, and an alert is recorded.
7. **Logging (SIEM):** The entire incident is saved permanently in our Database's Logs, so administrators can review what dangerous links users are encountering.
8. **Visualization:** The Frontend updates instantly, showing the user a beautiful "Risk Card" detailing the threat score, the action taken, and why the site was flagged.

---

## 3. The Technology Stack (What are we using?)

We divided the project into two independent halves: the **Frontend** (what you see) and the **Backend** (the logic and data processing). Let's look at the tools:

### Frontend (User Interface)
- **React.js:** A popular JavaScript library used to build interactive user interfaces. It allows us to create components (like buttons, navigation tabs, and risk cards) that update instantly without reloading the page.
- **Vite:** A blazing-fast build tool that starts up our React application instantly for development.
- **Tailwind CSS:** A modern styling system. Instead of writing separate, bulky CSS files, we use Tailwind to style our app directly in our code. It is what makes the platform look sleek, dark, and premium.
- **Axios:** A tiny library used by React to send HTTP requests to our backend API.

### Backend (The Brain & API)
- **Python:** The core programming language powering the backend, chosen because it is the undisputed king of Machine Learning.
- **FastAPI:** A modern, incredibly fast Python web framework. It creates the API endpoints (the "doors" the frontend knocks on to communicate) such as `/scan-url`, `/login`, and `/logs`.
- **Uvicorn:** The server software that actually runs our FastAPI application and keeps it listening for requests.
- **Pydantic:** Used natively by FastAPI to ensure the data coming in (like a user's password or a URL) is strictly formatted and valid.

### Machine Learning (The AI Engine)
- **Scikit-Learn (sklearn):** The primary Python library for Machine Learning. We use it to build our `RandomForestClassifier`.
- **Pandas & NumPy:** Data manipulation libraries. They act like super-powered Excel spreadsheets in code, helping us load, organize, and calculate the math behind our training data.
- **Joblib:** A tool used to compress and save our trained AI model into a dedicated file (`phishing_model.pkl`) so it doesn't have to relearn everything every time we start the server.

### Database & Security
- **SQLite:** A lightweight database that stores all our data (Usernames, Passwords, Security Logs) in a single file (`phishing.db`). 
- **SQLAlchemy:** An Object-Relational Mapper (ORM). It allows us to talk to the SQL database using normal Python code instead of writing raw SQL queries.
- **JWT (JSON Web Tokens) & Passlib:** This handles security securely. When a user registers, their password is encrypted (hashed). When they log in successfully, they are given a "token" (a digital VIP wristband) that proves who they are when they ask to view protected logs.

---

## 4. Pin-to-Pin Code Breakdown (What does each file do?)

If you look at the project folders, here is what every major piece is doing:

### 📂 `frontend/` Highlights
* **`src/App.jsx`**: The main gatekeeper. It holds the Router, deciding which page to show (Login, Register, or the Dashboard). It enforces protection—if you aren't logged in, it kicks you to the login screen.
* **`src/pages/UserScan.jsx`**: The main Dashboard page. It contains the large search bar, the scan button, the tabs (Dashboard, Logs, Settings), and the live clock.
* **`src/components/RiskCard.jsx`**: A reusable UI box that pops up after a scan, colored dynamically (Red for High Risk, Green for Low Risk) to show the threat details.
* **`src/services/api.js`**: The messenger. This file holds the code that talks to the FastAPI backend, making sure the user's security token is attached to every request.

### 📂 `backend/` Highlights
* **`main.py`**: The heart of the backend. It defines the routes (`@app.post("/scan-url")`, `@app.get("/logs")`) and pieces everything together. 
* **`model.py`**: The intelligence unit. It contains the logic to extract features from a URL (counting dots, finding IP formats, checking dictionaries). It loads our `.pkl` AI model and generates the final probability score. If the AI model fails or is missing, it contains a hardcoded fallback system (heuristics) to still guess the risk.
* **`generate_data.py`**: The data factory. This script generates thousands of synthetic "Good" URLs (like Amazon or Google API links) and thousands of "Malignant" URLs (punycode hacks, IP spoofs, typo-squatting). It builds the dataset the AI learns from.
* **`train_model.py`**: The AI school. This script loads the dataset created by the script above, teaches the Random Forest algorithm how to spot the difference between good and bad, tests the algorithm to ensure high accuracy, and exports the final `phishing_model.pkl` "brain".
* **`database.py` & `sql_models.py`**: Defines the blueprint for our data tables. It establishes the `users` table and the `scan_logs` table in our database.
* **`auth.py`**: Handles all the identity checks—verifying hashed passwords and generating standard JWT secure tokens.

---

## 5. Summary

The Cyber-Phish Platform is a complete, full-stack cybersecurity application. 

1. It has **Data Generation** to build its own knowledge base.
2. It has an **AI Training Pipeline** that results in a highly accurate predictive model.
3. It has a **FastAPI Web Server** that exposes this AI securely to the internet.
4. It features **Database Logging** and **Authentication** to protect who uses the platform and records what the platform blocks.
5. Finally, it ties it all together with a beautiful, responsive **React Web App** that makes interacting with complex machine learning as easy as pasting a link and clicking a button.
