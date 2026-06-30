# BookNest API Documentation

Base URL for all endpoints (when running locally): `http://127.0.0.1:8000`

> **Note on Authentication**: Most endpoints require a Bearer token in the `Authorization` header.
> Example: `Authorization: Bearer <your_access_token>`

---

## 1. Authentication

### `POST /signup`
Creates a new user account.
- **Body**: 
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "strongpassword"
  }
  ```

### `POST /login`
Authenticates a user and returns JWT tokens. Uses `x-www-form-urlencoded`.
- **Body**:
  - `username`: The user's email
  - `password`: The user's password
- **Returns**: `access_token`, `refresh_token`, `token_type`

### `GET /me`
Returns the currently authenticated user's information.
- **Headers**: `Authorization: Bearer <access_token>`

### `POST /refresh`
Generates a new access token using a refresh token.
- **Body**:
  ```json
  {
    "refresh_token": "<your_refresh_token>"
  }
  ```

---

## 2. Dashboard

### `GET /dashboard/stats`
Retrieves aggregated statistics for the current user's dashboard.
- **Headers**: `Authorization: Bearer <access_token>`
- **Returns**: `total_books`, `reading`, `finished`, `want_to_read`, `total_pages_read`, `average_rating`, `books_currently_lent`, `recent_activity` (array of actions).

---

## 3. Books

All routes require authentication.

### `GET /books`
Lists all books owned by the current user.
- **Query Params**:
  - `status` (optional): Filter by `READING`, `FINISHED`, `WANT_TO_READ`
  - `search` (optional): Search by title or author
  - `sort_by` (optional): `rating`, `title`, `date_added`
  - `skip` (optional, default 0)
  - `limit` (optional, default 100)

### `GET /books/{book_id}`
Gets details for a specific book.

### `POST /books`
Adds a new book.
- **Body**: 
  ```json
  {
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "status": "WANT_TO_READ",
    "rating": 5,
    "current_page": 0,
    "total_pages": 310
  }
  ```

### `PUT /books/{book_id}`
Updates a book.

### `DELETE /books/{book_id}`
Deletes a book.

---

## 4. Shelves

All routes require authentication.

### `GET /shelves`
Lists all custom shelves owned by the current user.

### `GET /shelves/{shelf_id}`
Gets details of a specific shelf, including the nested books.

### `POST /shelves`
Creates a new shelf.
- **Body**:
  ```json
  {
    "name": "Sci-Fi Favorites",
    "description": "My top science fiction picks"
  }
  ```

### `PUT /shelves/{shelf_id}`
Updates a shelf's name or description.

### `DELETE /shelves/{shelf_id}`
Deletes a shelf (does not delete the books inside it).

### `POST /shelves/{shelf_id}/books/{book_id}`
Adds an existing book to a shelf.

### `DELETE /shelves/{shelf_id}/books/{book_id}`
Removes a book from a shelf.

---

## 5. Sharing (RBAC)

Allows users to collaborate on shelves. All routes require authentication.

### `POST /sharing/shelves/{shelf_id}`
Shares a shelf with another user.
- **Body**:
  ```json
  {
    "email": "friend@example.com",
    "role": "viewer" // or "editor"
  }
  ```

### `GET /sharing/shared-with-me`
Retrieves all shelves that other users have shared with the current user.

### `PUT /sharing/{share_id}`
Updates a collaborator's role on a shelf (Owner only).
- **Body**:
  ```json
  {
    "role": "editor"
  }
  ```

### `DELETE /sharing/{share_id}`
Removes a collaborator's access to a shelf (Owner only).

---

## 6. Lending

Track physical books lent to friends. All routes require authentication.

### `GET /lending/borrowed`
Lists all books the current user is borrowing from others.

### `POST /lending/{book_id}/lend`
Lends a book to another user via their email.
- **Body**:
  ```json
  {
    "borrower_email": "friend@example.com"
  }
  ```

### `POST /lending/{lend_id}/return`
Marks a lent book as returned. Can be called by either the lender or the borrower.

---

## 7. WebSockets

Real-time activity and event streaming.

### `WS /ws/{user_id}`
Connects to the WebSocket server for real-time updates.
- Note: When implementing on the frontend, use the `WebSocket` API and connect to `ws://127.0.0.1:8000/ws/{user_id}`.
- Messages received will be JSON strings containing activity notifications (e.g., when a book is added or lent).
