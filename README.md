Baby Name App

A simple Flask web application to collaboratively review and vote on baby names.

Features
- Add names (comma or newline separated)
- Start a personal voting session (per user)
- Shuffled voting order per session
- Keyboard shortcuts: Left=No, Up=Undo, Down=Skip, Right=Yes
- Visible Undo button with tooltip
- Resume existing sessions and reset a user’s votes
- Results summary by user (Yes/No) with sorting (most likes, then both liked, then any votes, then name)
- Danish UI text
- Data persisted to a local JSON file

Requirements
- Python 3.10+
- pip

Setup
1. Create and activate a virtual environment (optional but recommended):
   python -m venv .venv
   .venv\Scripts\activate  (Windows)
   source .venv/bin/activate (macOS/Linux)

2. Install dependencies:
   pip install flask

Run
1. From the repository root, run:
   set PORT=5000  (Windows PowerShell; optional)
   set BABYNAME_SECRET=dev-secret-change-me  (optional)
   python -m flask --app BabyNameApp/BabyNameApp.py run --host 0.0.0.0 --port %PORT%

   Or directly:
   python BabyNameApp/BabyNameApp.py

2. Open the app in your browser:
   http://localhost:5000

Configuration
- BABYNAME_SECRET: Session secret key (default: dev-secret-change-me).
- DATA_FILE: The app writes to BabyNameApp/data.json next to the app file.

Usage
- Add names: Use the “Tilføj navne” page to paste names. They are deduplicated case-insensitively.
- Start: Enter your name and click Start. Use arrow keys to vote.
  - Nej (←), Fortryd (↑), Spring over (↓), Ja (→)
- Resume: On the Start page, click “Genoptag” next to your name.
- Reset: On the Start page, click “Nulstil” to clear a user’s votes.
- Results: See per-user likes and whether both liked a name.

Data persistence
- Votes and names are stored in BabyNameApp/data.json.
- To start fresh, delete data.json or use the Reset button per user.

Notes
- Debug mode is enabled by default when running directly. Disable for production.
- If you want to prevent accidental data writes, run without allowing writes (not implemented by default). You can add an env flag gate in save_data if needed.

License
- MIT (adjust as needed).