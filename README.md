# UNILAG Price Saver API

A high-performance backend service designed to help students in the University of Lagos reduce daily expenses by crowdsourcing, comparing, and predicting prices of items across campus.  
The system combines **FastAPI**, **SQLAlchemy**, and a **Rust-powered computation engine** for speed, scalability, and reliability.

## 🚀 Key Features

- Fast REST API built with **FastAPI**
- High-performance calculations using a **Rust PyO3 module**
- Machine learning predictions & location heatmaps
- Price comparison across vendors and student communities
- Squad payment integration for in-app transactions
- Automatic Python fallback when Rust engine is unavailable
- Fully modular architecture for easy scaling and maintenance

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
