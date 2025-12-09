# 🛒 UNILAG Price Saver API

> **Crowdsource, Compare, Save** — Empowering UNILAG students with real-time price intelligence across campus

A high-performance backend service that helps students make smarter purchasing decisions by crowdsourcing, comparing, and predicting prices of everyday items across the University of Lagos.

Built with **FastAPI** for blazing-fast APIs, **SQLAlchemy** for data integrity, and a **Rust-powered computation engine** for production-grade performance.

---

## ✨ Why UNILAG Price Saver?

### The Problem

- 📍 No transparent pricing across campus stores
- 💰 Students overpay without knowing better deals exist
- 🤝 No community-driven price intelligence
- 📊 Manual price tracking is tedious and unreliable

### The Solution

A **real-time, collaborative price discovery platform** that:

- 🗺️ Maps prices across all campus locations
- 🤖 Predicts fair prices using ML
- 👥 Leverages community feedback
- 💸 Helps students save money every day

---

## 🚀 Key Features

| Feature | What It Does |
|---------|-------------|
| 🗺️ **Interactive Location Picker** | Click on map or search to select store locations |
| 🔍 **Real-time Price Comparison** | View prices for same item across vendors |
| 🤖 **Price Predictions** | ML-powered fair price suggestions |
| 📍 **Heatmaps** | Visual price intensity across campus |
| 💬 **Community Reviews** | Crowdsourced feedback on prices & quality |
| 💳 **Integrated Payments** | Squad API for in-app transactions |
| ⚡ **Lightning Fast** | Rust engine for complex calculations |
| 🌙 **Dark Mode** | Beautiful, modern dark UI |
| 📱 **Mobile Responsive** | Works seamlessly on all devices |
| 🔐 **Secure** | Role-based access, data validation |

## 📦 Architecture Overview

| Component | Technology | Description |
|----------|------------|-------------|
| **API Layer** | FastAPI | Handles requests, routing, and validation |
| **Database** | SQLite (default) | Stores items, prices, users, and analytics |
| **Computation Engine** | Rust (PyO3) | Heavy calculations, stats, predictions |
| **ORM** | SQLAlchemy | Models, migrations, DB interactions |
| **ML Layer** | Python + optional Rust | Predictions, heatmaps |
| **Payments** | Squad API | Payment link generation |

## 📁 Project Structure

```text
app/
 ├── routers/
 │    ├── items.py
 │    ├── prices.py
 │    ├── payments.py
 │    └── ml.py
 ├── services/
 │    ├── price_engine.py
 │    ├── heatmap_engine.py
 │    └── squad.py
 ├── models.py
 ├── database.py
 └── main.py
rust_engine/
 └── src/lib.rs
README.md
requirements.txt
```

## 🛠 Prerequisites

- Python **3.9+**
- Rust **1.70+**
- pip
- maturin (recommended for building the Rust engine)

## 📥 Install Python Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Building the Rust Engine

### Option 1: maturin (recommended)

```bash
pip install maturin
cd rust_engine
maturin develop
cd ..
```

### Option 2: cargo build

```bash
cd rust_engine
cargo build --release
```

Windows output typically appears at:

```text
rust_engine/target/release/rust_engine.pyd
```

Copy it into the project root or `site-packages`.

## ▶️ Running the API

Start the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python -m uvicorn app.main:app --reload
```

**Local URL:** <http://localhost:8000>
**Swagger UI:** <http://localhost:8000/docs>
**ReDoc:** <http://localhost:8000/redoc>

## 📡 API Endpoints

### Items

- `GET /items` — List items  
- `POST /items` — Create item  

### Prices

- `GET /prices` — Get price entries  
- `POST /prices` — Submit price data  

### Payments

- `POST /payments/pay` — Generate payment link  

### Machine Learning

- `GET /ml/predict` — Predict item price  
- `GET /ml/heatmap` — Generate price heatmap  

## ⚡ Rust Engine Functions

The compiled module exposes:

- `cheapest(prices: Vec<f64>) -> f64`
- `savings(current: f64, cheapest: f64) -> f64`
- `predict_price(item: str, location: str) -> f64`
- `aggregate_stats(prices: Vec<f64>, quantities: Vec<i64>) -> Dict`
- `weighted_average_price(prices, quantities) -> f64`

Rust is used for:

- Stats aggregation  
- Price predictions  
- Weighted averages  
- Heatmap calculations  
- Any heavy numeric operations

## 🧩 Extending the Rust Module

Add a new function in `rust_engine/src/lib.rs`:

```rust
#[pyfunction]
fn my_calculation(data: Vec<f64>) -> f64 {
    // implementation
}
```

Rebuild:

```bash
cd rust_engine
maturin develop
```

Use in Python:

```python
import rust_engine
rust_engine.my_calculation([1.0, 2.0, 3.0])
```

## 💾 Database Configuration

Default:

```text
sqlite:///./prices.db
```

Override using env variable:

```bash
set DATABASE_URL=sqlite:///./prices.db
```

Or modify `app/database.py`.

## 🐞 Troubleshooting

### ModuleNotFoundError: rust_engine

Run:

```bash
cd rust_engine
maturin develop
```

### ImportError in ML

Confirm the following exist:

```text
app/services/heatmap_engine.py
app/services/price_engine.py
app/services/squad.py
```

### datetime.utc error

Use:

```python
datetime.utcnow()
```

Already patched in `app/models.py`.

## 📄 License

MIT License

## 📬 Contact

For issues, suggestions, or contributions, reach out to the **UNILAG Price Saver Development Team**.
