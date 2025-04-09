# NoGateList Architecture Documentation

This document outlines the architecture of NoGateList, a collaborative list application that allows users to create and share lists without requiring login.

## Application Overview

NoGateList is built with a FastAPI backend, Supabase database, and vanilla JavaScript frontend. The application allows users to create ephemeral lists identified by unique codes, which can be shared with others for collaboration.

## System Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Client Browser │◄────►│  FastAPI Server │◄────►│     Supabase    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
    │                                                      ▲
    │                                                      │
    ▼                                                      │
┌─────────────────┐                              ┌─────────────────┐
│                 │                              │                 │
│   LocalStorage  │                              │ Database Tables │
│                 │                              │                 │
└─────────────────┘                              └─────────────────┘
```

### Key Components

1. **FastAPI Server**: Handles HTTP requests, renders templates, and manages data
2. **Supabase Database**: Stores lists and items data
3. **Client-side JavaScript**: Manages UI interactions and local data
4. **LocalStorage**: Tracks recently visited lists on the client

## Directory Structure

```
/
├── app/
│   ├── __init__.py            # Package initialization
│   ├── main.py                # FastAPI application and routes
│   ├── config.py              # Configuration settings
│   └── static/                # Static assets
│       ├── css/
│       │   └── styles.css     # Application styling
│       └── js/
│           └── main.js        # Client-side JavaScript
├── templates/                 # Jinja2 HTML templates
│   ├── index.html             # Home page template
│   └── list.html              # List view template
└── IMPROVEMENT_ROADMAP.md     # Future improvement ideas
```

## Data Model

### Database Tables

#### Lists Table
- `id` (UUID): Primary key
- `code` (TEXT): Unique shareable code
- `name` (TEXT): List name
- `created_at` (TIMESTAMP): Creation timestamp
- `expiry_date` (TIMESTAMP): Expiration timestamp (typically 7 days from creation)

#### Items Table
- `id` (UUID): Primary key
- `list_id` (UUID): Foreign key to Lists table
- `content` (TEXT): Item content
- `completed` (BOOLEAN): Completion status
- `created_at` (TIMESTAMP): Creation timestamp

## Key Workflows

### List Creation
1. User clicks "Create New List" button
2. Server generates a unique code
3. A new list record is created in the database
4. User is redirected to the list page
5. List is added to LocalStorage for recent lists tracking

### List Access
1. User enters a list code or clicks a recent list
2. Server checks if the list exists
   - If exists: displays the list
   - If not exists: creates a new list with that code
3. List items are fetched and displayed
4. List information is updated in LocalStorage

### Item Management
1. Adding items: POST to `/lists/{code}/items`
2. Toggling completion: POST to `/lists/{code}/items/{item_id}/toggle`
3. Deleting items: POST to `/lists/{code}/items/{item_id}/delete`

## Frontend Components

### Core JavaScript Functionality
- **Copy Functionality**: Clipboard API for sharing list codes and URLs
- **Form Animations**: Visual feedback during form submissions
- **Recent Lists Management**: LocalStorage API for tracking history
- **Item Interactions**: Toggle animations and deletion confirmation
- **Search Functionality**: Filtering lists by name or code

### UI Components
- **App Container**: Main application wrapper
- **List Interface**: Items display with toggle and delete controls
- **Copied Feedback**: Notification system for clipboard operations
- **Expiry Badges**: Visual indicators of list expiration status

## Backend Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page |
| `/lists/create` | GET/POST | Create a new list |
| `/lists/join` | POST | Join an existing list |
| `/lists/{code}` | GET | View a specific list |
| `/lists/{code}/update` | POST | Update list name |
| `/lists/{code}/items` | POST | Add a new item |
| `/lists/{code}/items/{item_id}/toggle` | POST | Toggle item completion |
| `/lists/{code}/items/{item_id}/delete` | POST | Delete an item |
| `/lists/{code}/delete` | POST | Delete a list |

## Lifecycle Management

- Lists automatically expire after 7 days
- A cleanup function runs on page load to remove expired lists
- The client shows expiry information with color-coded indicators
- LocalStorage entries persist regardless of server-side expiration 