# NoGateList

A collaborative list application that enables real-time list sharing without requiring user accounts. Built with FastAPI and Supabase.

## Features

- Create and share lists without user accounts
- Real-time synchronization across devices
- Access lists using unique codes
- Automatic list persistence
- Add, check off, and delete list items
- Remember previously accessed lists

## Tech Stack

- Backend: Python FastAPI
- Database: Supabase (PostgreSQL)
- Real-time: Supabase Realtime
- Frontend: HTML, CSS, JavaScript
- Local Storage: Browser localStorage for remembering lists

## Setup

1. Install Python 3.8+ and pip
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
NoGateList/
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration and environment variables
│   ├── database.py       # Supabase client and database operations
│   ├── models.py         # Pydantic models
│   └── static/           # Static files (CSS, JS)
│       ├── css/
│       └── js/
└── templates/            # HTML templates
```

## Database Schema

```sql
create table lists (
    id uuid default gen_random_uuid() primary key,
    code text unique not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

create table items (
    id uuid default gen_random_uuid() primary key,
    list_id uuid references lists(id) on delete cascade,
    content text not null,
    completed boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License