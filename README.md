## TradeX Stock Portfolio Simulator

TradeX is a **React + FastAPI + PostgreSQL** single-page web application for simulating stock trading.  
Users can register, log in, trade virtual stocks with dynamic prices, and track their portfolio value, cash, and total profit/loss with visual analytics.

### Tech Stack
- **Frontend**: React, Vite (or CRA), Axios, Recharts, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL

### Features
- **Authentication**: Signup with unique email, login via username or email, logout.
- **Trading**: Buy/sell stocks with dynamic pricing (volatility + market impact).
- **Portfolio**:
  - Current holdings and cash balance
  - Total portfolio value and total profit/loss
  - Allocation and sector breakdown charts
- **UI/UX**:
  - Modern login/signup screens (TradeX branding)
  - Responsive dashboard and portfolio views

---

## Project Structure
- `backend/` – FastAPI app, models, schemas, and routes.
- `client/` – React SPA (login, signup, dashboard, portfolio, trading modal).

---

## Prerequisites
- **Node.js** (LTS recommended)
- **Python 3.10+**
- **PostgreSQL**

---

## Backend Setup (FastAPI)

1. **Create and configure database**
   - Create a PostgreSQL database (for example: `stock_app_db`).
   - Ensure the connection URL in `backend/database.py` (and `backend/add_email_column.py`) matches your local setup, e.g.  
     `postgresql://postgres:YOUR_PASSWORD@localhost/stock_app_db`.

2. **Create virtual environment & install dependencies**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Run database migrations**
- First-time create tables (if not already created by the app).
- Run the email migration (if needed):

```bash
python add_email_column.py
```

4. **Start FastAPI server**

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

---

## Frontend Setup (React)

1. **Install dependencies**

```bash
cd client
npm install
```

2. **Configure API base URL (if needed)**
- Check the API base URL used in the React services/components (e.g. `axios` calls) and point it to `http://127.0.0.1:8000`.

3. **Start the React dev server**

```bash
npm run dev
```

The app will be available at the URL printed in the terminal (commonly `http://localhost:5173` for Vite).

---

## Running the Full App
1. Start **FastAPI backend** (`uvicorn`) on port `8000`.
2. Start **React frontend** (`npm run dev`) in the `client` folder.
3. Open the frontend URL in your browser, then:
   - Sign up (TradeX account),
   - Log in,
   - Trade stocks and explore the dashboard/portfolio analytics.

---

## Notes
- This project is for **educational use** (course project) and does not execute real trades.
- For production, you should:
  - Use **hashed passwords** and stronger auth (JWT, OAuth2).
  - Store secrets (DB URL, keys) in environment variables.
  - Add proper error handling, logging, and security hardening.


