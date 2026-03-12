# Project Setup & Execution

### 1. Environment Setup
Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a .env file in the root directory and add your credentials:
```bash
AICORE_AUTH_URL=
AICORE_CLIENT_ID=
AICORE_CLIENT_SECRET=
AICORE_RESOURCE_GROUP=
AICORE_BASE_URL=
```

### 4. Usage
* **Run Main Code:**
  ```bash
  python test_sap.py
  ```

* **Cleanup Data:**
  To delete collections or documents, reference the logic in:
  ```bash
  python cleanup.py
  ```
