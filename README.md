# BazaarAi — AI-Powered Shopping Assistant 🛒✨

*Shop Smarter with AI*

BazaarAi is a full-stack, autonomous conversational e-commerce assistant built with FastAPI, SQLite, and Groq-powered multimodal LLMs. It features visual product recognition, intelligent multi-attribute catalog filtering, transparent step-by-step agent reasoning, side-by-side product comparisons, order tracking, coupon validation, and an interactive luxury shopping interface.

---

## 🌟 Key Features

- **Multimodal Visual Product Search**: Upload any photo of a product (shoes, electronics, appliances, lifestyle items) to analyze visual attributes and instantly retrieve similar items from the catalog.
- **Autonomous Multi-Step Agent Reasoning**: Powered by Groq LLM (`qwen/qwen3.8-27b`) with transparent reasoning traces displaying steps, tools, and observations.
- **Side-by-Side Product Comparisons**: Automatically builds feature matrices, price deltas, and recommendation verdicts between competing items.
- **Smart Catalog & Sentiment Search**: Multi-attribute filtering (category, price range, star ratings, organic certifications) combined with aggregated customer reviews and sentiment analysis.
- **Order Tracking & Management**: Live order lookup with checkpoint timelines, carrier details, and estimated delivery dates.
- **Cart & Instant Checkout**: Persistent cart drawer, subtotal calculation, coupon discounts (`BAZAAR10`), and 1-click checkout.
- **Database & Inventory Manager**: In-app modal to browse, search, add, or remove products from the SQLite database.
- **Persistent Chat History**: Real-time conversation storage in SQLite with session restoration and search palette (⌘K).

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLite3, Pydantic
- **AI & Multimodal Vision**: Groq API, LangChain, Pillow
- **Frontend**: Vanilla HTML5, CSS3 (Luxury Dark Theme), JavaScript (ES6+)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/premshaw04/BazaarAI.git
cd BazaarAI
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Add your Groq API Key (get one for free at [console.groq.com](https://console.groq.com/keys)):
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Initialize Database (Optional)
If you wish to reset or re-seed the product database:
```bash
python setup_db.py
```

### 5. Start the Application
```bash
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
```
http://localhost:8000
```

---

## 📁 Project Structure

```
├── server.py              # FastAPI backend & REST API endpoints
├── agent_engine.py        # Autonomous agent engine, tools & multimodal vision
├── setup_db.py            # SQLite schema initialization & sample data seeder
├── store.db               # SQLite database (products, reviews, orders, chats)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── static/
│   ├── index.html         # Single-page web application UI
│   ├── style.css          # Luxury dark design system & responsive styling
│   ├── app.js             # Frontend controller, state & event engine
│   ├── images/            # Brand logos & product catalog media
│   └── uploads/           # User-uploaded images
└── README.md              # Project documentation
```

---

## 📜 License
This project is open-source and available under the MIT License.
