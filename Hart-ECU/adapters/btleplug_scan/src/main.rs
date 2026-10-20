//! Read-only BLE discovery sidecar for cross-language clients.
//!
//! This process scans advertisements and reports device metadata only. It deliberately does not
//! connect to a peripheral, discover GATT services, read/write characteristics, or issue ECU data.
//! The source was statically reviewed against btleplug 0.13.5 but could not be compiled here because
//! rustc/cargo are unavailable. Treat it as an uncompiled sample until target builds pass.

use std::io::{self, BufRead};
use std::time::Duration;

use btleplug::api::{Central, Manager as _, Peripheral, ScanFilter};
use btleplug::platform::Manager;
use serde_json::{json, Value};
use tokio::time::sleep;

fn error_response(id: Value, code: i64, message: impl Into<String>) -> Value {
    json!({
        "jsonrpc": "2.0",
        "id": id,
        "error": {"code": code, "message": message.into()}
    })
}

fn success_response(id: Value, result: Value) -> Value {
    json!({"jsonrpc": "2.0", "id": id, "result": result})
}

async fn list_adapters(id: Value) -> Value {
    let manager = match Manager::new().await {
        Ok(value) => value,
        Err(error) => return error_response(id, -32000, format!("BLE manager: {error}")),
    };
    let adapters = match manager.adapters().await {
        Ok(value) => value,
        Err(error) => return error_response(id, -32000, format!("BLE adapter enumeration: {error}")),
    };

    let mut items = Vec::new();
    for (index, adapter) in adapters.iter().enumerate() {
        let info = adapter.adapter_info().await.unwrap_or_else(|e| format!("unavailable: {e}"));
        let state = adapter.adapter_state().await.map(|s| format!("{s:?}"))
            .unwrap_or_else(|e| format!("unavailable: {e}"));
        items.push(json!({"index": index, "info": info, "state": state}));
    }
    success_response(id, json!({
        "adapters": items,
        "connect_enabled": false,
        "gatt_read_enabled": false,
        "gatt_write_enabled": false
    }))
}

async fn scan(id: Value, params: &Value) -> Value {
    let seconds = match params.get("seconds") {
        None => 5,
        Some(value) => match value.as_u64() {
            Some(seconds) => seconds,
            None => return error_response(id, -32602, "seconds must be an integer from 1 through 30"),
        },
    };
    if !(1..=30).contains(&seconds) {
        return error_response(id, -32602, "seconds must be an integer from 1 through 30");
    }
    let manager = match Manager::new().await {
        Ok(value) => value,
        Err(error) => return error_response(id, -32000, format!("BLE manager: {error}")),
    };
    let adapters = match manager.adapters().await {
        Ok(value) => value,
        Err(error) => return error_response(id, -32000, format!("BLE adapter enumeration: {error}")),
    };

    let mut scanned_adapters = Vec::new();
    let mut devices = Vec::new();
    for (index, adapter) in adapters.iter().enumerate() {
        let info = adapter.adapter_info().await.unwrap_or_else(|e| format!("unavailable: {e}"));
        if let Err(error) = adapter.start_scan(ScanFilter::default()).await {
            scanned_adapters.push(json!({"index": index, "info": info, "scan_error": error.to_string()}));
            continue;
        }
        sleep(Duration::from_secs(seconds)).await;
        let peripherals = match adapter.peripherals().await {
            Ok(value) => value,
            Err(error) => {
                let stop_result = adapter.stop_scan().await;
                scanned_adapters.push(json!({
                    "index": index,
                    "info": info,
                    "enumeration_error": error.to_string(),
                    "stop_scan_error": stop_result.err().map(|e| e.to_string())
                }));
                continue;
            }
        };
        let stop_error = adapter.stop_scan().await.err().map(|e| e.to_string());
        scanned_adapters.push(json!({
            "index": index,
            "info": info,
            "peripherals_seen": peripherals.len(),
            "stop_scan_error": stop_error
        }));

        for peripheral in peripherals {
            let properties = peripheral.properties().await.ok().flatten();
            let connected = peripheral.is_connected().await.ok();
            let local_name = properties.as_ref().and_then(|p| p.local_name.clone());
            let rssi = properties.as_ref().and_then(|p| p.rssi);
            let advertised_services: Vec<String> = properties.as_ref()
                .map(|p| p.services.iter().map(ToString::to_string).collect())
                .unwrap_or_default();
            devices.push(json!({
                "adapter_index": index,
                "peripheral_id": peripheral.id().to_string(),
                "address": peripheral.address().to_string(),
                "local_name": local_name,
                "rssi_dbm": rssi,
                "advertised_services": advertised_services,
                "already_connected": connected
            }));
        }
    }

    success_response(id, json!({
        "scan_seconds_per_adapter": seconds,
        "adapters": scanned_adapters,
        "devices": devices,
        "connect_enabled": false,
        "gatt_read_enabled": false,
        "gatt_write_enabled": false
    }))
}

async fn handle(request: Value) -> Value {
    let id = request.get("id").cloned().unwrap_or(Value::Null);
    let valid_id = request.get("id").is_some_and(|value| value.is_null() || value.is_string() || value.is_number());
    if !valid_id || request.get("jsonrpc").and_then(Value::as_str) != Some("2.0") {
        return error_response(id, -32600, "Invalid JSON-RPC request");
    }
    let method = match request.get("method").and_then(Value::as_str) {
        Some(value) => value,
        None => return error_response(id, -32600, "method must be a string"),
    };
    let params = request.get("params").cloned().unwrap_or_else(|| json!({}));
    if !params.is_object() {
        return error_response(id, -32602, "params must be an object");
    }
    match method {
        "ble.adapters.list" => {
            if !params.as_object().is_some_and(|p| p.is_empty()) {
                return error_response(id, -32602, "ble.adapters.list takes no parameters");
            }
            list_adapters(id).await
        }
        "ble.scan" => {
            let unknown: Vec<&str> = params.as_object().into_iter().flat_map(|p| p.keys())
                .filter(|key| key.as_str() != "seconds").map(String::as_str).collect();
            if !unknown.is_empty() {
                return error_response(id, -32602, format!("unsupported parameter(s): {}", unknown.join(", ")));
            }
            scan(id, &params).await
        }
        _ => error_response(id, -32601, format!("Unknown method: {method}")),
    }
}

#[tokio::main]
async fn main() {
    for line in io::stdin().lock().lines() {
        let response = match line {
            Ok(input) => match serde_json::from_str::<Value>(&input) {
                Ok(request) => handle(request).await,
                Err(error) => error_response(Value::Null, -32700, format!("JSON parse error: {error}")),
            },
            Err(error) => error_response(Value::Null, -32000, format!("stdin error: {error}")),
        };
        println!("{response}");
    }
}
