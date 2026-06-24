# Vega API — Authentication

The Vega API uses Bearer token authentication. Every request must include the
`Authorization: Bearer <token>` header.

## Getting a token
Send a POST /auth/login with email and password. The response returns:
- access_token: valid for 1 hour.
- refresh_token: valid for 30 days.

## Refreshing the token
When the access_token expires, use POST /auth/refresh sending the refresh_token.
There is no need to send email and password again.

## Common errors
- 401 Unauthorized: token missing, invalid, or expired.
- 403 Forbidden: valid token, but no permission for the resource.
