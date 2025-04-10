from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
import string
import os
import uvicorn
from dotenv import load_dotenv
from supabase import create_client
from .config import settings
from datetime import datetime, timedelta
import pytz

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Get the absolute path to the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="NoGateList", root_path=os.environ.get("ROOT_PATH", ""))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "app/static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(ROOT_DIR, "templates"))

# Models for Supabase (for reference)
# Lists table: id (uuid), code (text), created_at (timestamp), name (text), expiry_date (timestamp)
# Items table: id (uuid), list_id (uuid), content (text), completed (boolean), created_at (timestamp)

def generate_code(length: int = 6) -> str:
    """Generate a random access code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def format_date(date_str):
    """Format date string to human-readable format."""
    if not date_str:
        return "Unknown"
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%b %d, %Y")
    except Exception:
        return date_str

def get_days_remaining(date_str):
    """Calculate days remaining until expiry."""
    if not date_str:
        return 0
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now(pytz.utc)
        days = (date_obj - now).days
        return max(0, days)
    except Exception:
        return 0

# Check for expired lists
def cleanup_expired_lists():
    """Delete expired lists."""
    now = datetime.now(pytz.utc).isoformat()
    supabase.table('lists').delete().lt('expiry_date', now).execute()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Run cleanup
    cleanup_expired_lists()
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/lists/create")
async def create_list():
    while True:
        code = generate_code()
        # Check if code exists
        result = supabase.table('lists').select("*").eq('code', code).execute()
        if not result.data:
            break
    
    # Calculate expiry date (7 days from now)
    expiry_date = (datetime.now(pytz.utc) + timedelta(days=7)).isoformat()
    
    # Insert new list with default name and expiry
    supabase.table('lists').insert({
        "code": code,
        "name": "Untitled List",
        "expiry_date": expiry_date
    }).execute()
    
    # Redirect to the list page
    return RedirectResponse(f"/lists/{code}", status_code=303)

@app.get("/lists/create")
async def create_list_get():
    # Reuse the same logic as POST
    return await create_list()

@app.post("/lists/join")
async def join_list(request: Request, code: str = Form(...)):
    # Check if the list exists
    result = supabase.table('lists').select("*").eq('code', code).execute()
    if not result.data:
        # Redirect back with an error message
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error_message": "The list with the provided code does not exist. Please try again."
            }
        )
    
    return RedirectResponse(f"/lists/{code}", status_code=303)

@app.get("/lists/{code}", response_class=HTMLResponse)
async def get_list(request: Request, code: str):
    # Run cleanup
    cleanup_expired_lists()
    
    # Check if the list exists
    result = supabase.table('lists').select("*").eq('code', code).execute()
    if not result.data:
        # Create the list if it doesn't exist
        expiry_date = (datetime.now(pytz.utc) + timedelta(days=7)).isoformat()
        supabase.table('lists').insert({
            "code": code,
            "name": "Untitled List",
            "expiry_date": expiry_date
        }).execute()
        result = supabase.table('lists').select("*").eq('code', code).execute()
    
    list_id = result.data[0]['id']
    list_name = result.data[0].get('name', 'Untitled List')
    expiry_date = result.data[0].get('expiry_date')
    formatted_expiry_date = format_date(expiry_date)
    days_remaining = get_days_remaining(expiry_date)
    
    items_result = supabase.table('items').select("*").eq('list_id', list_id).execute()
    
    # Get error message from query params if any
    error_message = request.query_params.get("error", "")
    
    return templates.TemplateResponse(
        "list.html", 
        {
            "request": request, 
            "code": code,
            "name": list_name,
            "items": items_result.data,
            "expiry_date": formatted_expiry_date,
            "days_remaining": days_remaining,
            "error_message": error_message
        }
    )

@app.post("/lists/{code}/update")
async def update_list(request: Request, code: str, name: str = Form(...)):
    # Update list name
    print(f"Updating list name for code {code} to: {name}")
    
    try:
        # Get the list first to verify it exists
        result = supabase.table('lists').select("*").eq('code', code).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="List not found")
        
        list_id = result.data[0]['id']
        print(f"Found list with ID: {list_id}")
        
        # Perform the update using the list_id to be extra safe
        update_result = supabase.table('lists').update({
            "name": name
        }).eq('code', code).execute()
        
        print(f"Update result: {update_result}")
        
        # Verify the update
        verify_result = supabase.table('lists').select("*").eq('code', code).execute()
        if verify_result.data:
            print(f"Updated list name: {verify_result.data[0].get('name')}")
    except Exception as e:
        print(f"Error updating list name: {str(e)}")
    
    return RedirectResponse(f"/lists/{code}", status_code=303)

@app.post("/lists/{code}/items")
async def add_item(code: str, content: str = Form(...)):
    try:
        if not content or content.strip() == "":
            # Redirect back with error
            return RedirectResponse(f"/lists/{code}?error=Content+is+required", status_code=303)
        
        # Get list id
        result = supabase.table('lists').select("*").eq('code', code).execute()
        if not result.data:
            return RedirectResponse(f"/lists/{code}?error=List+not+found", status_code=303)
        
        list_id = result.data[0]['id']
        
        # Insert item
        insert_result = supabase.table('items').insert({
            "list_id": list_id,
            "content": content.strip(),
            "completed": False
        }).execute()
        
        if not insert_result.data:
            return RedirectResponse(f"/lists/{code}?error=Failed+to+add+item", status_code=303)
        
        return RedirectResponse(f"/lists/{code}", status_code=303)
    except Exception as e:
        print(f"Error adding item: {str(e)}")
        return RedirectResponse(f"/lists/{code}?error=An+error+occurred", status_code=303)

@app.post("/lists/{code}/items/{item_id}/toggle")
async def toggle_item(code: str, item_id: str):
    # Get current state
    result = supabase.table('items').select("*").eq('id', item_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = result.data[0]
    new_state = not item["completed"]
    
    # Update item
    supabase.table('items').update({
        "completed": new_state
    }).eq('id', item_id).execute()
    
    return RedirectResponse(f"/lists/{code}", status_code=303)

@app.post("/lists/{code}/items/{item_id}/delete")
async def delete_item(code: str, item_id: str):
    supabase.table('items').delete().eq('id', item_id).execute()
    return RedirectResponse(f"/lists/{code}", status_code=303)

@app.post("/lists/{code}/delete")
async def delete_list(code: str):
    # Check if the list exists
    result = supabase.table('lists').select("*").eq('code', code).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Delete the list (will cascade delete items due to foreign key constraint)
    supabase.table('lists').delete().eq('code', code).execute()
    
    return RedirectResponse("/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)