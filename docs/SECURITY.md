# Security Notes

This project is designed as a safe, local-only assistant for a developer portfolio and demos.

## Important constraints

- No unrestricted shell execution.
- No `eval` or `exec` execution of user content.
- Only registered tools are allowed.
- File access is limited to safe directories and supported extensions.
- The project does not expose real secrets in storage or logs.

## Remaining limitations

This project is not a public Internet service and should not be deployed without additional hardening, authentication, rate limiting, and deployment review.
