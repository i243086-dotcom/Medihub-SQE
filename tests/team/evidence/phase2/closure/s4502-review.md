# S4502 technical review

Candidate `a7c2d00fc79247b3e3c3067b59e93fc9d7f91975`. Finding `python:S4502` at Flask app construction. **Evidence supports a false-positive disposition for authenticated CSRF in this application configuration. Independent approval is pending.** The alert remains open, including on the disposable CI scanner. The quality threshold stays at security A.

## Source and executed checks

| Surface | Source mechanism | Executed evidence |
|---|---|---|
| All 14 protected write paths | Flask JWT accepts only the Authorization Bearer header. Patient, doctor and admin decorators validate JWT and role before reaching the handler. The assembled Flask URL map is checked against the exact write-route inventory. | On each route, a valid JWT in an access cookie alone returned 401. A valid cookie for the intended role plus a wrong-role header returned 403. SQLite row counts and appointment state were unchanged. |
| Login | Public endpoint reads JSON credentials and returns the JWT in the JSON body. The browser stores it in localStorage and explicitly attaches it to same-origin API requests. | Form-encoded login returned 400. A valid JSON login set no cookie. Its bearer worked on /me, and a subsequent request without the header returned 401. |
| Registration | Public endpoint reads JSON and assigns the patient role explicitly. It creates an account and patient row without authenticating the browser. | Form-encoded registration returned 415 and wrote no rows. JSON registration created the intended two rows, set no cookie and produced no JWT. /me returned 401. |
| Logout | Public endpoint is a stateless acknowledgement. The application JavaScript removes its localStorage token after the call. | POST returned 200, set no cookie, and left database counts and appointment state unchanged. |
| CORS and frontend | The Flask app has no CORS middleware or allow-origin configuration. The application uses relative /api URLs and explicitly sets Content-Type and Authorization. | Cross-origin preflights for login, register, patient booking and both staff status endpoints received no allow-origin or allow-credentials header. |

The audit found no Flask session use or cookie-setting call in shipped handlers. Static and SPA routes are GET-only. Offline seeding, migration and Celery functions are outside the Flask request route inventory. These findings apply to the checked application build. The deployment owner must confirm that a future proxy or authentication integration does not add an ambient credential or permissive CORS policy.

No finding was dismissed. The reviewer should compare deployed configuration with the checked source, confirm the route and cookie assertions, and record a reasoned approval or request corrections on PR #11. The ephemeral CI instance also needs an approved way to retain any future disposition before a green release can be claimed.

[JWT configuration](../../../../../backend/app.py#L24) · [Role decorators](../../../../../backend/decorators.py) · [Public auth handlers](../../../../../backend/routes/auth.py) · [Same-origin browser client](../../../../../frontend/js/api.js) · [Route inventory and assertions](../../../api/test_auth_transport.py) · [Backend execution JUnit](verified/backend/junit.xml)

[Flask-JWT-Extended configuration](https://flask-jwt-extended.readthedocs.io/en/stable/options.html) · [OWASP CSRF prevention guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

