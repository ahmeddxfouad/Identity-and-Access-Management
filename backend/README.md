# Coffee Shop Backend

Flask API that serves drinks and recipes with **Auth0 JWT + RBAC**.

## Run

```bash
cd backend
python3 -m venv env && source env/bin/activate      # Windows: py -m venv env && .\env\Scripts\Activate.ps1
pip install -r requirements.txt
export FLASK_APP=api.py
export AUTH0_DOMAIN="YOUR_TENANT.eu.auth0.com"
export API_AUDIENCE="coffeeshop"                    # must match your Auth0 API Identifier
export ALGORITHMS="RS256"
cd src
# First run only: uncomment db_drop_and_create_all() in api.py to seed, then re-comment.
flask run --reload
```

## Environment Variables
- `AUTH0_DOMAIN` – e.g., `dev-ahmeddxfouad.eu.auth0.com`
- `API_AUDIENCE` – must equal your Auth0 API Identifier (e.g., `coffeeshop`)
- `ALGORITHMS` – `RS256`

## Endpoints
- `GET /drinks` (public) → short representation
- `GET /drinks-detail` (requires `get:drinks-detail`) → long representation
- `POST /drinks` (requires `post:drinks`) → returns new drink (long)
- `PATCH /drinks/<id>` (requires `patch:drinks`) → returns updated drink (long)
- `DELETE /drinks/<id>` (requires `delete:drinks`) → returns deleted id

### Response Examples

**GET /drinks**
```json
{
  "success": true,
  "drinks": [
    { "id": 1, "title": "Cappuccino", "recipe": [{ "color": "#a67c52", "parts": 1 }] }
  ]
}
```

**Errors**
```json
{ "success": false, "error": 401, "message": "unauthorized" }
{ "success": false, "error": 403, "message": "permission not found" }
{ "success": false, "error": 404, "message": "resource not found" }
{ "success": false, "error": 422, "message": "unprocessable" }
```

## Auth

`src/auth/auth.py` implements:
- `get_token_auth_header()` – extracts `Bearer <JWT>`
- `verify_decode_jwt(token)` – fetches JWKS, verifies RS256, audience/issuer
- `check_permissions(permission, payload)` – ensures permissions claim includes required scope
- `@requires_auth("scope")` – route decorator

## Data Model
`src/database/models.py` contains `Drink` with `insert()`, `update()`, `delete()`, `short()`, `long()` helpers.

## CORS
`flask-cors` is enabled; ensure headers `Content-Type, Authorization` and methods `GET,POST,PATCH,DELETE,OPTIONS` are allowed.