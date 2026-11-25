# SonarQube issue review

The evidence in this folder belongs to the final candidate. The earlier review project exports under `../sonar/` preserve the full-scope intermediate analysis and screenshots. The original application database was never used for static analysis or scanner-side tests.

| Initial confirmed finding | Remediation | Verification |
|---|---|---|
| Hard-coded Flask and JWT key material and predictable provisioned credentials | Configure keys from the protected environment, with independent random local fallback. Bootstrap no longer creates an account with a default password. Demo seed requires explicit passwords and admin-created doctor passwords are randomized. | Full-scope scan, active login checks, and 30 Chromium flows. Existing stored credentials require separate rotation before deployment. |
| Debug defaults and unrestricted CORS | Remove always-on debug configuration and the wildcard CORS setup. The bundled Vue application uses the same origin. | Full-scope scan and actual browser login/booking/cancellation. |
| Four CDN assets with no integrity binding | Pin Vue to the verified version and use SHA-384 integrity and anonymous CORS for the four scanner-reported assets. | Computed hashes of exact CDN payloads. Chromium passed against the same bytes with integrity enforcement. |
| Unlabelled inputs, duplicate JS definitions and ignored promise failures | Associate labels, retain effective last implementations and explicitly handle rejection. | Full-scope rescan reported zero bugs and reliability A. |
| `python:S4502` CSRF | Reviewed individually. Appointment writes authenticate using a JWT in an explicit Authorization header. There is no cookie JWT transport, the browser calls the same origin, and permissive CORS was removed. This supports a potential false-positive disposition for authenticated endpoints, subject to a genuine independent review of all request paths. | The issue remains OPEN. The CI security gate expects A and returned D. No issue was reclassified or suppressed to pass the gate. |

The residual smells concern UTC API style and JavaScript number parsing. A project review can address them separately. Both real issue listings and the hotspot export are retained. SonarQube’s native gate and the additional agreed project-wide gate are separate conditions. The initial trial with a broad test inclusion dropped backend Python. Its apparent pass was rejected and the scan was repeated with directory-specific test classification and required source/coverage checks.

[JWT configuration options](https://flask-jwt-extended.readthedocs.io/en/stable/options.html) · [OWASP CSRF prevention guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
