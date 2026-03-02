"""
NTDF Digital Net Analysis API - Simplified Version
Phase 1: Basic API endpoints
Created: 2026-02-22
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
import yfinance as yf
import json

# API Keys
ALPHA_VANTAGE_API_KEY = "X9GC2MV7P1GCODRZ"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Models
class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
    timestamp: str

# ============ FastAPI App ============
app = FastAPI(title="NTDF API", version="1.0.0")

# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Health Check ============
@app.get("/health", tags=["root"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "backend": "running",
            "alpha_vantage": "available",
            "yahoo_finance": "available"
        }
    }

# ============ Root Path ============
@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "NTDF Digital Net Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "health": "/health",
            "alpha_vantage_quote": "/api/market/alpha_vantage/quote",
            "yahoo_quote": "/api/market/yahoo/quote",
            "alpha_vantage_daily": "/api/market/alpha_vantage/daily",
            "yahoo_daily": "/api/market/yahoo/daily",
            "yahoo_intraday": "/api/market/yahoo/intraday",
            "sma": "/api/indicators/sma",
            "ema": "/api/indicators/ema",
            "rsi": "/api/indicators/rsi"
        }
    }

# ============ Alpha Vantage Endpoints ============

@app.get("/api/market/alpha_vantage/quote", tags=["market"])
async def get_alpha_vantage_quote(symbol: str) -> Dict[str, Any]:
    """Get Alpha Vantage real-time quote"""
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Global Quote" in data:
            quote = data["Global Quote"]
            return {
                "success": True,
                "symbol": symbol,
                "company": quote.get("01. symbol", ""),
                "price": float(quote.get("05. price", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "open": float(quote.get("02. open", 0)),
                "volume": int(quote.get("06. volume", 0)),
                "timestamp": quote.get("07. latest trading day", "")
            }
        else:
            return {
                "success": False,
                "error": "No quote data found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/market/alpha_vantage/daily", tags=["market"])
async def get_alpha_vantage_daily(symbol: str, outputsize: str = "compact") -> Dict[str, Any]:
    """Get Alpha Vantage daily data"""
    try:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": outputsize
        }

        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            return {
                "success": True,
                "symbol": symbol,
                "interval": "daily",
                "data": time_series,
                "length": len(time_series)
            }
        else:
            return {
                "success": False,
                "error": "No time series data found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/market/alpha_vantage/intraday", tags=["market"])
async def get_alpha_vantage_intraday(symbol: str, interval: str = "1min") -> Dict[str, Any]:
    """Get Alpha Vantage intraday data"""
    try:
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "interval": interval
        }

        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if f"Time Series ({interval})" in data:
            time_series = data[f"Time Series ({interval})"]
            return {
                "success": True,
                "symbol": symbol,
                "interval": interval,
                "data": time_series,
                "length": len(time_series)
            }
        else:
            return {
                "success": False,
                "error": "No intraday data found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============ Yahoo Finance Endpoints ============

@app.get("/api/market/yahoo/quote", tags=["market"])
async def get_yahoo_quote(symbol: str) -> Dict[str, Any]:
    """Get Yahoo Finance real-time quote"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")

        if not hist.empty:
            latest = hist.iloc[-1]
            return {
                "success": True,
                "symbol": symbol,
                "company_name": "",
                "current_price": float(latest['Close']),
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "volume": int(latest['Volume']),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "No data available"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/market/yahoo/daily", tags=["market"])
async def get_yahoo_daily(symbol: str, period: str = "1mo") -> Dict[str, Any]:
    """Get Yahoo Finance daily data"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if not hist.empty:
            data_list = []
            for index, row in hist.iterrows():
                data_list.append({
                    "date": index.strftime("%Y-%m-%d"),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "adj_close": float(row['Adj Close']),
                    "volume": int(row['Volume'])
                })

            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "data": data_list,
                "length": len(data_list)
            }
        else:
            return {
                "success": False,
                "error": "No data available"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/market/yahoo/intraday", tags=["market"])
async def get_yahoo_intraday(symbol: str, period: str = "5d") -> Dict[str, Any]:
    """Get Yahoo Finance intraday data"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if not hist.empty:
            data_list = []
            for index, row in hist.iterrows():
                data_list.append({
                    "timestamp": index.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "adj_close": float(row['Adj Close']),
                    "volume": int(row['Volume'])
                })

            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "data": data_list,
                "length": len(data_list)
            }
        else:
            return {
                "success": False,
                "error": "No data available"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============ Technical Indicators ============

@app.get("/api/indicators/sma", tags=["indicators"])
async def calculate_sma(symbol: str, period: int = 20) -> Dict[str, Any]:
    """Calculate Simple Moving Average (SMA)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"3mo")

        if not hist.empty:
            closes = hist['Close'].tolist()

            sma_values = []
            for i in range(len(closes)):
                if i >= period:
                    window = closes[i-period:i]
                    ma = sum(window) / period
                else:
                    ma = None
                sma_values.append(ma)

            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "sma": sma_values,
                "current_sma": sma_values[-1] if sma_values else None
            }
        else:
            return {
                "success": False,
                "error": "No data available"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/indicators/ema", tags=["indicators"])
async def calculate_ema(symbol: str, period: int = 20) -> Dict[str, Any]:
    """Calculate Exponential Moving Average (EMA)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"3mo")

        if not hist.empty:
            closes = hist['Close'].tolist()

            # Calculate multiplier
            multiplier = 2 / (period + 1)

            # Calculate EMA
            ema_values = []
            ema = closes[0]
            ema_values.append(ema)

            for price in closes[1:]:
                ema = (price - ema) * multiplier + ema
                ema_values.append(ema)

            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "ema": ema_values,
                "current_ema": ema_values[-1] if ema_values else None
            }
        else:
            return {
                "success": False,
                "error": "No data available"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/indicators/rsi", tags=["indicators"])
async def calculate_rsi(symbol: str, period: int = 14) -> Dict[str, Any]:
    """Calculate Relative Strength Index (RSI)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"6mo")

        if not hist.empty:
            closes = hist['Close'].tolist()

            # Calculate deltas
            deltas = []
            for i in range(1, len(closes)):
                deltas.append(closes[i] - closes[i-1])

            gains = []
            losses = []

            for delta in deltas:
                if delta > 0:
                    gains.append(delta)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(delta))

            avg_gains = sum(gains[-period:]) / period
            avg_losses = sum(losses[-period:]) / period

            # Calculate RSI
            if avg_losses == 0:
                rsi = 100
            else:
                rs = avg_gains / avg_losses
                rsi = 100 - (100 / (1 + rs))

            rsi_values = []
            for delta in deltas:
                if delta > 0:
                    avg_gains = ((avg_gains * (period - 1)) + delta) / period
                else:
                    avg_losses = ((avg_losses * (period - 1)) + abs(delta)) / period

                if avg_losses == 0:
                    rsi = 100
                else:
                    rs = avg_gains / avg_losses
                    rsi = 100 - (100 / (1 + rs))

                rsi_values.append(rsi)

            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "rsi": rsi_values,
                "current_rsi": rsi_values[-1] if rsi_values else None
            }
        else:
            return {
                "success": False,
                "error": "No data available"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============ Main Server ============
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting NTDF Backend Server...")
    print(f"Address: http://0.0.0.0:8000")
    print(f"API Docs: http://0.0.0.0:8000/docs")
    print(f"Health: http://0.0.0.0:8000/health")
    print("")
    print("✅ Server started successfully!")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
