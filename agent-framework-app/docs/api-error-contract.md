# API Error Contract (Story S8)

Defines the unified structure for error responses returned by the backend API.

## Goals

- Consistent client handling
- Clear machine readable error codes
- Human friendly messages for logs / UI mapping layer

## Error Response Schema

```json
{
  "error": {
    "code": "E_<DOMAIN>_<IDENTIFIER>",
    "http_status": 400,
    "message": "Human readable summary (not for i18n yet)",
    "details": {"optional": "context object"},
    "correlation_id": "uuid-v4",
    "ts": "ISO8601"
  }
}
```

## Code Taxonomy (Initial)

| Domain | Prefix | Example | Description |
|--------|--------|---------|-------------|
| Validation | VAL | `E_VAL_REQUIRED_FIELD` | Missing required field |
| Auth | AUTH | `E_AUTH_INVALID_TOKEN` | Token invalid/expired |
| Resource | RES | `E_RES_NOT_FOUND` | Entity not found |
| Internal | INT | `E_INT_UNEXPECTED` | Generic fall-through |

> Additional domains will be appended as features expand.

## Normalization Responsibilities

- Translate framework / library exceptions to contract
- Ensure unknown exceptions map to `E_INT_UNEXPECTED` with minimal leak
- Always attach `correlation_id` (middleware generated)

## Testing Guidelines

- Unit tests assert mapping of representative internal exceptions → contract payload
- Snapshot test for canonical 400 + 404 + 500 responses

## Future Extensions

- Localization token layering
- RFC 9457 (Problem Details) compatibility adapter
- Metrics tagging (code, domain)
