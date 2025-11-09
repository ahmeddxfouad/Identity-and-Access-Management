# Coffee Shop Full Stack

A secure, RBAC-protected **Flask API** + **Ionic (Angular) frontend** for a coffee shop menu.

- **Public** users: view drink names + graphics (ratios).
- **Barista** role: view full recipes.
- **Manager** role: create, edit, delete drinks.
- **Auth0 (JWT + RBAC)** secures the API; the UI hides actions the user isn’t permitted to do.

---

## Quick Start

### 1) Backend (Flask)
```bash
cd backend
python3 -m venv env && source env/bin/activate     # Windows: py -m venv env && .\env\Scripts\Activate.ps1
pip install -r requirements.txt
export FLASK_APP=api.py
export AUTH0_DOMAIN="YOUR_TENANT.eu.auth0.com"
export API_AUDIENCE="coffeeshop"                   # must match your Auth0 API Identifier
export ALGORITHMS="RS256"
cd src
flask run --reload
```

### 2) Frontend (Ionic/Angular)
```bash
cd frontend
npm install
export NODE_OPTIONS=--openssl-legacy-provider      # only if Node >= 17
ionic serve                                        # serves at http://localhost:8100
```

---

## Auth0 Setup (summary)

1. **Create a SPA application** (Angular).
   - **Allowed Callback URLs**
     - `http://localhost:8100` (or your exact callback path, e.g., `/login-results`)
   - **Allowed Logout URLs**: `http://localhost:8100`
   - **Allowed Web Origins**: `http://localhost:8100`
   - **Allowed Origins (CORS)**: `http://localhost:8100`

2. **Create an API**
   - **Identifier (Audience)**: `coffeeshop` (or choose another, but use it everywhere)
   - **Signing Algorithm**: RS256
   - Enable **RBAC** and **Add Permissions in the Access Token**.

3. **Permissions**
   - `get:drinks`, `get:drinks-detail`, `post:drinks`, `patch:drinks`, `delete:drinks`

4. **Roles**
   - **Barista** → `get:drinks`, `get:drinks-detail`
   - **Manager** → all five permissions

5. **Users**
   - Create two users in **Username-Password-Authentication** connection and assign the roles.

---

## Endpoints (expected)
- `GET /drinks` (public)
- `GET /drinks-detail` (requires `get:drinks-detail`)
- `POST /drinks` (requires `post:drinks`)
- `PATCH /drinks/<id>` (requires `patch:drinks`)
- `DELETE /drinks/<id>` (requires `delete:drinks`)

---

## Project Structure
```
.
├── backend/                 # Flask API
│   ├── requirements.txt
│   └── src/
│       ├── api.py
│       ├── auth/auth.py
│       └── database/models.py
├── frontend/                # Ionic Angular app
│   └── src/environment/environment.ts
└── udacity-fsnd-udaspicelatte.postman_collection.json
```

---

## Troubleshooting

**Callback URL mismatch**  
- The `redirect_uri` sent by the app must **exactly** match an entry in Auth0 “Allowed Callback URLs” (scheme, host, port, path).  
- Use `http://localhost:8100/...` for Ionic dev (not `https://`).

**401 / 403 with tokens**  
- Ensure the **audience** in frontend matches the Auth0 API Identifier and backend `API_AUDIENCE`.  
- Confirm RBAC and “Add Permissions in the Access Token” are enabled.  
- Assign the correct role to the user.

**CORS errors**  
- Ensure `flask-cors` is enabled and allow `Authorization` header.  
- Add `http://localhost:8100` to Allowed Web Origins/Origins (CORS) in Auth0.

---

## Postman
- Import `udacity-fsnd-udaspicelatte.postman_collection.json`.
- Set Barista/Manager tokens on their folders.
- Export and overwrite the same file path for submission.