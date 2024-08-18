
### `API_DOCS.md`

```markdown
User Service API Documentation

Overview
API documentation for the User Service, which manages user data, reviews, orders, and wishlists.

Version: 1.0.0
API Specification: OpenAPI 3.1

Authentication
Method: OAuth2 Password Bearer
Token URL: /token
Authorization Header: Authorization: Bearer <token>

Most endpoints in this service require a valid JWT token passed in the Authorization header.

Endpoints

User Management Endpoints

Read User
- URL: /users/{user_id}
- Method: GET
- Summary: Retrieve user information by user ID.
- Parameters:
  - user_id (integer): The ID of the user.
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/UserRead"
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Read Users Me
- URL: /users/me
- Method: GET
- Summary: Retrieve the authenticated user's information.
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/UserRead"
    }

Update User Me
- URL: /users/me
- Method: PUT
- Summary: Update the authenticated user's information.
- Request Body:
  {
    "$ref": "#/components/schemas/UserUpdate"
  }
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/UserRead"
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Read Public Profile
- URL: /users/{username}/profile
- Method: GET
- Summary: Retrieve the public profile of a user by username.
- Parameters:
  - username (string): The username of the user.
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/UserRead"
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Protected Endpoint
- URL: /users/protected-endpoint
- Method: GET
- Summary: Access a protected endpoint for authenticated users.
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/UserRead"
    }

Review Management Endpoints

Create Review
- URL: /reviews/
- Method: POST
- Summary: Create a new review for a product or vendor.
- Request Body:
  {
    "$ref": "#/components/schemas/ReviewCreate"
  }
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/ReviewRead"
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Get Reviews
- URL: /reviews/products/{product_id}/reviews
- Method: GET
- Summary: Retrieve reviews for a specific product.
- Parameters:
  - product_id (integer): The ID of the product.
- Response:
  - 200 Successful Response:
    {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ReviewRead"
      }
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Order Management Endpoints

Create Order
- URL: /orders/orders/
- Method: POST
- Summary: Create a new order for a product.
- Request Body:
  {
    "$ref": "#/components/schemas/OrderCreate"
  }
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/Order"
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Get User Orders
- URL: /orders/orders/{user_id}
- Method: GET
- Summary: Retrieve all orders placed by a specific user.
- Parameters:
  - user_id (integer): The ID of the user.
- Response:
  - 200 Successful Response:
    {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/Order"
      }
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Wishlist Management Endpoints

Add To Wishlist
- URL: /wishlist/wishlist/
- Method: POST
- Summary: Add a product to the user's wishlist.
- Request Body:
  {
    "$ref": "#/components/schemas/WishlistCreate"
  }
- Response:
  - 200 Successful Response:
    {
      "$ref": "#/components/schemas/WishlistRead"
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Get User Wishlist
- URL: /wishlist/wishlist/{user_id}
- Method: GET
- Summary: Retrieve the wishlist of a specific user.
- Parameters:
  - user_id (integer): The ID of the user.
- Response:
  - 200 Successful Response:
    {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/WishlistRead"
      }
    }
  - 422 Validation Error:
    {
      "$ref": "#/components/schemas/HTTPValidationError"
    }

Miscellaneous Endpoints

Read Root
- URL: /
- Method: GET
- Summary: Root endpoint.
- Response:
  - 200 Successful Response:
    {}
