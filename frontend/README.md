# Coffee Shop Frontend (Ionic Angular)

Ionic/Angular app that authenticates with **Auth0** and calls the Flask API.

## Setup & Run
```bash
cd frontend
npm install
export NODE_OPTIONS=--openssl-legacy-provider   # only if Node >= 17
ionic serve                                     # http://localhost:8100
```

## Configure Auth0
Edit `src/environment/environment.ts`:
```ts
export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000',
  auth0: {
    url: 'YOUR_TENANT.eu.auth0.com',        // full domain (no protocol)
    audience: 'coffeeshop',                 // must match API Identifier
    clientId: 'YOUR_SPA_CLIENT_ID',
    callbackURL: 'http://localhost:8100'    // or exact callback path used by the app
  }
};
```

### Auth0 Application Settings
- **Allowed Callback URLs**: include the exact `redirect_uri` your app sends (e.g., `http://localhost:8100` or `/login-results` path).
- **Allowed Logout URLs**: `http://localhost:8100`
- **Allowed Web Origins**: `http://localhost:8100`
- **Allowed Origins (CORS)**: `http://localhost:8100`

## Dev Tokens (optional helper)
The starter can read tokens from `localStorage`:
```js
localStorage.setItem('JWTS_LOCAL_KEY', JSON.stringify(['<BARISTA_JWT>', '<MANAGER_JWT>']));
localStorage.setItem('JWTS_ACTIVE_INDEX_KEY', '0'); // or '1'
location.reload();
```

## Common Issues
- **Callback URL mismatch**: The `redirect_uri` must exactly match an Allowed Callback URL.
- **CORS**: Make sure the backend allows `Authorization` header and Auth0 has your origin in Web Origins/CORS.
- **403 Forbidden**: Verify the user role and that your JWT contains the required permission claim.