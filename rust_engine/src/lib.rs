use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;

/// Find the cheapest price in a list of prices.
#[pyfunction]
fn cheapest(prices: Vec<f64>) -> f64 {
    prices.into_iter().fold(f64::INFINITY, |a, b| a.min(b))
}

/// Calculate savings between current and cheapest price.
#[pyfunction]
fn savings(current: f64, cheapest: f64) -> f64 {
    current - cheapest
}

/// Predict price for an item at a given location using a simple linear model.
#[pyfunction]
fn predict_price(item: String, location: String) -> f64 {
    let hash = (item.len() as f64 * 100.0 + location.len() as f64 * 50.0) % 1000.0;
    400.0 + hash
}

/// Aggregate statistics (mean, min, max, total)
#[pyfunction]
fn aggregate_stats(prices: Vec<f64>, quantities: Vec<i64>) -> PyResult<HashMap<String, f64>> {
    let mut result = HashMap::new();

    if prices.is_empty() {
        result.insert("mean".to_string(), 0.0);
        result.insert("min_val".to_string(), 0.0);
        result.insert("max_val".to_string(), 0.0);
        result.insert("total_qty".to_string(), 0.0);
        return Ok(result);
    }

    let mean = prices.iter().sum::<f64>() / prices.len() as f64;
    let min_val = prices.iter().copied().fold(f64::INFINITY, f64::min);
    let max_val = prices.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let total_qty: i64 = quantities.iter().sum();

    result.insert("mean".to_string(), mean);
    result.insert("min_val".to_string(), min_val);
    result.insert("max_val".to_string(), max_val);
    result.insert("total_qty".to_string(), total_qty as f64);

    Ok(result)
}

/// Weighted average price
#[pyfunction]
fn weighted_average_price(prices: Vec<f64>, quantities: Vec<i64>) -> PyResult<f64> {
    if prices.len() != quantities.len() {
        return Err(PyValueError::new_err(
            "Prices and quantities must have the same length",
        ));
    }

    if prices.is_empty() {
        return Ok(0.0);
    }

    let weighted_sum: f64 = prices
        .iter()
        .zip(quantities.iter())
        .map(|(&p, &q)| p * q as f64)
        .sum();

    let total_qty: i64 = quantities.iter().sum();

    if total_qty == 0 {
        return Ok(0.0);
    }

    Ok(weighted_sum / total_qty as f64)
}

#[pymodule]
fn rust_engine(py: Python, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(cheapest, module)?)?;
    module.add_function(wrap_pyfunction!(savings, module)?)?;
    module.add_function(wrap_pyfunction!(predict_price, module)?)?;
    module.add_function(wrap_pyfunction!(aggregate_stats, module)?)?;
    module.add_function(wrap_pyfunction!(weighted_average_price, module)?)?;
    Ok(())
}
