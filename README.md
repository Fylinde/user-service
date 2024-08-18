# User Service

## Overview

The User Service is a critical component of our microservices architecture, responsible for managing user-related data, including user profiles, reviews, orders, and wishlists. This service provides the necessary endpoints to create, read, update, and manage user information as well as user interactions with products and vendors.

## Features

- **User Management**: Retrieve and update user profile information.
- **Review Management**: Create and retrieve reviews for products and vendors.
- **Order Management**: Create and retrieve orders placed by users.
- **Wishlist Management**: Manage user wishlists, including adding products to wishlists and retrieving wishlist items.

## Purpose

The User Service is designed to handle all user-related data and operations, providing a robust API for managing users, their interactions, and preferences. This service is crucial for ensuring that users can efficiently interact with the system, leave reviews, place orders, and manage their wishlists.

## Usage

This service is used by the frontend application to interact with user data, enabling features such as user profile management, order tracking, and wishlist functionality. It also allows users to create and manage product reviews.

## Endpoints Overview

For a detailed list of available endpoints, including request and response formats, please refer to the [API Documentation](./API_DOCS.md).

## Technologies

- **OAuth2**: Used for secure authorization, enabling users to log in and receive tokens that provide access to protected endpoints.
- **REST API**: The service exposes a RESTful API for interaction with other services and clients.

## Setup and Configuration

To set up the User Service, follow these steps:

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/your-org/user-service.git
