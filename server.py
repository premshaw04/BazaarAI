import os
import re
import sqlite3
import json
import base64
import shutil
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

import shopping_agent
from agent_engine import agent_engine

app = FastAPI(title="BazaarAI - AI Shopping Assistant")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(BASE_DIR, "store.db")
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = []
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    session_id: Optional[str] = None


class SaveChatRequest(BaseModel):
    id: str
    title: Optional[str] = None
    messages: List[Dict[str, Any]]


def get_relative_time(dt_str: str) -> str:
    try:
        # Support formats like '2026-10-08 03:30:00' or ISO
        dt = datetime.fromisoformat(dt_str)
    except Exception:
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Recently"

    diff = datetime.now() - dt
    secs = max(0, diff.total_seconds())
    if secs < 60:
        return "Just now"
    elif secs < 3600:
        m = int(secs // 60)
        return f"{m} min ago" if m == 1 else f"{m} mins ago"
    elif secs < 86400:
        h = int(secs // 3600)
        return f"{h} hour ago" if h == 1 else f"{h} hours ago"
    else:
        d = int(secs // 86400)
        return f"{d} day ago" if d == 1 else f"{d} days ago"


@app.get("/")
def get_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/chats")
def get_all_chats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC LIMIT 30")
    rows = cursor.fetchall()
    conn.close()

    chats = []
    for r in rows:
        chats.append({
            "id": r["id"],
            "title": r["title"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "time_ago": get_relative_time(r["updated_at"]),
        })
    return {"chats": chats}


@app.get("/api/chats/{session_id}")
def get_chat_session(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Chat session not found")

    try:
        msgs = json.loads(row["messages"])
    except Exception:
        msgs = []

    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "messages": msgs,
    }


@app.post("/api/chats")
def save_chat_session(payload: SaveChatRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    title = payload.title
    if not title:
        # Determine title from first user message
        for m in payload.messages:
            if m.get("role") == "user" and m.get("content"):
                c = m.get("content").strip()
                title = c[:30] + ("..." if len(c) > 30 else "")
                break
    if not title:
        title = "New Shopping Chat"

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT id, created_at FROM chat_sessions WHERE id = ?", (payload.id,))
    existing = cursor.fetchone()

    msgs_json = json.dumps(payload.messages)
    if existing:
        cursor.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = ?, messages = ? WHERE id = ?",
            (title, now_iso, msgs_json, payload.id),
        )
    else:
        cursor.execute(
            "INSERT INTO chat_sessions (id, title, created_at, updated_at, messages) VALUES (?, ?, ?, ?, ?)",
            (payload.id, title, now_iso, now_iso, msgs_json),
        )

    conn.commit()
    conn.close()
    return {"success": True, "id": payload.id, "title": title}


@app.delete("/api/chats/{session_id}")
def delete_chat_session(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Chat {session_id} deleted"}


@app.delete("/api/chats")
def clear_all_chats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions")
    conn.commit()
    conn.close()
    return {"success": True, "message": "All chat history cleared"}


@app.get("/api/products")
def list_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if query:
        sql += " AND (name LIKE ? OR description LIKE ? OR category LIKE ? OR brand LIKE ?)"
        term = f"%{query}%"
        params.extend([term, term, term, term])

    if category:
        sql += " AND category = ?"
        params.append(category)

    if brand:
        sql += " AND brand = ?"
        params.append(brand)

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)

    if min_rating is not None:
        sql += " AND rating >= ?"
        params.append(min_rating)

    sql += " ORDER BY rating DESC, price ASC LIMIT 20"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    products = [dict(row) for row in rows]
    return {"products": products}


@app.get("/api/products/{product_id}")
def get_product_details(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    prod = cursor.fetchone()
    if not prod:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    cursor.execute("SELECT * FROM reviews WHERE product_id = ? ORDER BY rating DESC", (product_id,))
    reviews = [dict(r) for r in cursor.fetchall()]
    conn.close()

    result = dict(prod)
    result["reviews"] = reviews
    return result


@app.post("/api/checkout")
def checkout(payload: Dict[str, Any]):
    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="Missing product_id")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
    prod = cursor.fetchone()
    if not prod:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    name = prod["name"]
    price = prod["price"]

    cursor.execute(
        "INSERT INTO orders (product_id, product_name, price) VALUES (?, ?, ?)",
        (product_id, name, price),
    )
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "success": True,
        "order_id": order_id,
        "product_name": name,
        "price": price,
        "message": f"Order #{order_id} placed successfully for '{name}' (₹{price:,.2f})!",
    }


@app.get("/api/orders")
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"orders": orders}


@app.post("/api/products")
def create_product(payload: Dict[str, Any]):
    name = payload.get("name")
    category = payload.get("category", "general")
    price = float(payload.get("price", 0))
    if not name or price <= 0:
        raise HTTPException(status_code=400, detail="Product name and valid price are required")

    mrp = float(payload.get("mrp") or price)
    discount_pct = int(payload.get("discount_pct") or 0)
    rating = float(payload.get("rating") or 4.5)
    review_count = int(payload.get("review_count") or 100)
    brand = payload.get("brand", "")
    image_url = payload.get("image_url", "/static/images/honey.png")
    description = payload.get("description", "")
    is_organic = 1 if payload.get("is_organic") else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, price, description, is_organic, mrp, discount_pct, rating, review_count, brand, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, price, description, is_organic, mrp, discount_pct, rating, review_count, brand, image_url))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"success": True, "id": new_id, "message": f"Product '{name}' added successfully!"}


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Product #{product_id} deleted"}


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    safe_name = f"upload_{int(datetime.now().timestamp())}{ext}"
    dest_path = os.path.join(UPLOADS_DIR, safe_name)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": safe_name,
        "url": f"/static/uploads/{safe_name}",
        "local_path": dest_path,
    }


@app.get("/api/settings")
def get_settings():
    has_key = bool(os.environ.get("GROQ_API_KEY", "").strip())
    masked = ""
    if has_key:
        k = os.environ.get("GROQ_API_KEY", "")
        masked = k[:6] + "..." + k[-4:] if len(k) > 10 else "***"
    return {"has_groq_key": has_key, "masked_key": masked}


@app.post("/api/settings")
def save_settings(payload: Dict[str, str]):
    api_key = payload.get("groq_api_key", "").strip()
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
        env_path = os.path.join(BASE_DIR, ".env")
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"GROQ_API_KEY={api_key}\n")
        except Exception as e:
            print("Failed to save to .env:", e)
        return {"success": True, "message": "Groq API key configured and saved to .env!"}
    return {"success": False, "message": "API key cannot be empty"}


def parse_query_and_search(query_str: str) -> List[Dict[str, Any]]:
    """Smart database query parser for instant product matching."""
    conn = get_db_connection()
    cursor = conn.cursor()

    q_lower = query_str.lower()

    # Extract price constraint e.g. "under 3000", "under 60000", "less than 20k"
    max_price = None
    price_match = re.search(r"(?:under|below|less than|<|within)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|lakh)?", q_lower)
    if price_match:
        val = float(price_match.group(1).replace(",", ""))
        unit = price_match.group(2)
        if unit == "k":
            val *= 1000
        elif unit == "lakh":
            val *= 100000
        max_price = val
    elif "60k" in q_lower:
        max_price = 60000
    elif "20k" in q_lower:
        max_price = 20000
    elif "3000" in q_lower:
        max_price = 3000

    # Category matching
    target_category = None
    if any(k in q_lower for k in ["shoe", "sneaker", "running", "shoes", "footwear"]):
        target_category = "shoes"
    elif any(k in q_lower for k in ["laptop", "notebook", "computer", "pc", "macbook"]):
        target_category = "laptops"
    elif any(k in q_lower for k in ["phone", "smartphone", "mobile", "iphone", "samsung", "redmi", "oneplus", "pixel"]):
        target_category = "smartphones"
    elif any(k in q_lower for k in ["headphone", "earphone", "audio", "earbuds", "airpods"]):
        target_category = "headphones"
    elif any(k in q_lower for k in ["kitchen", "home", "fryer", "cooker", "vacuum", "mixer", "geyser", "microwave", "appliance"]):
        target_category = "kitchen"
    elif any(k in q_lower for k in ["watch", "smartwatch", "wearable", "tracker", "garmin"]):
        target_category = "smartwatch"
    elif any(k in q_lower for k in ["gaming", "game", "controller", "ps5", "xbox", "mouse", "keyboard"]):
        target_category = "gaming"
    elif any(k in q_lower for k in ["honey", "raw honey"]):
        target_category = "honey"
    elif any(k in q_lower for k in ["oil", "olive oil"]):
        target_category = "oil"
    elif any(k in q_lower for k in ["nut", "almond", "cashew"]):
        target_category = "nuts"
    elif any(k in q_lower for k in ["tea", "coffee", "sencha", "espresso"]):
        target_category = "tea"
    elif any(k in q_lower for k in ["oat", "quinoa", "grain", "cereal"]):
        target_category = "grains"

    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if target_category:
        sql += " AND category = ?"
        params.append(target_category)

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)

    if "organic" in q_lower:
        sql += " AND is_organic = 1"

    if "rating" in q_lower or "rated" in q_lower or "best" in q_lower:
        sql += " AND rating >= 4.0"

    # If no specific category matched, try keyword search
    if not target_category:
        words = [w for w in re.findall(r"\w+", q_lower) if w not in ["show", "me", "want", "find", "good", "best", "the", "with", "under", "in", "for"]]
        if words:
            word_clauses = []
            for w in words:
                word_clauses.append("(name LIKE ? OR description LIKE ? OR category LIKE ? OR brand LIKE ?)")
                params.extend([f"%{w}%", f"%{w}%", f"%{w}%", f"%{w}%"])
            sql += " AND (" + " OR ".join(word_clauses) + ")"

    sql += " ORDER BY rating DESC, price ASC LIMIT 8"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    session_id = req.session_id or f"chat_{int(datetime.now().timestamp()*1000)}"

    # Determine image path if provided or present in message
    img_path = req.image_path
    img_url = req.image_url
    if not img_path:
        img_match = re.search(r"((?:upload_\d+|cat_\w+|[a-zA-Z0-9_\-]+)\.(?:png|jpg|jpeg|webp))", user_msg, re.IGNORECASE)
        if img_match:
            fname = img_match.group(1)
            c1 = os.path.join(UPLOADS_DIR, fname)
            c2 = os.path.join(STATIC_DIR, "images", fname)
            if os.path.exists(c1):
                img_path = c1
                if not img_url:
                    img_url = f"/static/uploads/{fname}"
            elif os.path.exists(c2):
                img_path = c2
                if not img_url:
                    img_url = f"/static/images/{fname}"

    # Run the full agentic system engine
    agent_output = agent_engine.run(
        message=user_msg,
        history=req.history,
        session_id=session_id,
        image_path=img_path,
        image_url=img_url,
    )

    now_str = agent_output.get("timestamp") or datetime.now().strftime("%I:%M %p").lstrip("0")

    # Persist session into SQLite
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_entry = {"role": "user", "content": user_msg, "timestamp": now_str}
        if img_url:
            user_entry["image_url"] = img_url
        if img_path:
            user_entry["image_path"] = img_path

        updated_history = list(req.history)
        updated_history.append(user_entry)
        updated_history.append(agent_output)

        first_prompt = ""
        for m in updated_history:
            if m.get("role") == "user" and m.get("content"):
                first_prompt = m["content"]
                break
        title = (first_prompt[:28] + ("..." if len(first_prompt) > 28 else "")) if first_prompt else "Shopping Chat"

        cur.execute("SELECT id FROM chat_sessions WHERE id = ?", (session_id,))
        if cur.fetchone():
            cur.execute(
                "UPDATE chat_sessions SET title = ?, updated_at = ?, messages = ? WHERE id = ?",
                (title, now_iso, json.dumps(updated_history), session_id),
            )
        else:
            cur.execute(
                "INSERT INTO chat_sessions (id, title, created_at, updated_at, messages) VALUES (?, ?, ?, ?, ?)",
                (session_id, title, now_iso, now_iso, json.dumps(updated_history)),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Session save error:", e)

    return agent_output
