# eBikeR API Reference

## Authentication Endpoints
- `POST /api/users/token/` - Obtain JWT access/refresh tokens.
- `POST /api/users/token/refresh/` - Refresh JWT token.
- `POST /api/users/register/` - Register new user account.

## E-Bike Endpoints
- `GET /api/bikes/` - List all e-bikes with filtering and search.
- `POST /api/bikes/` - Create a new e-bike (Admin only).
- `GET /api/bikes/{id}/` - Retrieve e-bike details and telemetry.

## Bookings Endpoints
- `GET /api/bookings/` - List user rentals and bookings.
- `POST /api/bookings/` - Create a new bike rental booking.
