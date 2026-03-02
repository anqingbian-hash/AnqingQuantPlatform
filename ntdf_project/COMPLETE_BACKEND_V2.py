from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests
import yfinance as yf

app = FastAPI(title="NTDF API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}

@app.get("/")
async def root():
    return {"message": "NTDF API", "version": "2.0.0", "docs": "/docs", "health": "/health"}

@app.get("/api/market/alpha_vantage/quote")
async def get_alpha_vantage_quote(symbol: str):
    try:
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": "X9GC2MV7P1GCODRZ"}
        response = requests.get("https://www.alphavantage.co/query", params=params, timeout=10)
        data = response.json()
        if "Global Quote" in data:
            quote = data["Global Quote"]
            return {"success": True, "symbol": symbol, "price": float(quote.get("05. price", 0))}
        return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/market/alpha_vantage/daily")
async def get_alpha_vantage_daily(symbol: str, outputsize: str = "compact"):
    try:
        params = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": "X9GC2MV7P1GCODRZ", "outputsize": outputsize}
        response = requests.get("https://www.alphavantage.co/query", params=params, timeout=10)
        data = response.json()
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            return {"success": True, "symbol": symbol, "interval": "daily", "data": time_series}
        return {"success": False, "error": "No time series data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/market/yahoo/quote")
async def get_yahoo_quote(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            latest = hist.iloc[-1]
            return {"success": True, "symbol": symbol, "price": float(latest['Close'])}
        return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/market/yahoo/daily")
async def get_yahoo_daily(symbol: str, period: str = "1mo"):
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
            return {"success": True, "symbol": symbol, "period": period, "data": data_list}
        return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/indicators/sma")
async def calculate_sma(symbol: str, period: int = 20):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
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
            return {"success": True, "symbol": symbol, "period": period, "sma": sma_values, "current_sma": sma_values[-1] if sma_values else None}
        return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/indicators/ema")
async def calculate_ema(symbol: str, period: int = 20):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        if not hist.empty:
            closes = hist['Close'].tolist()
            multiplier = 2 / (period + 1)
            ema_values = []
            ema = closes[0]
            ema_values.append(ema)
            for price in closes[1:]:
                ema = (price - ema) * multiplier + ema
                ema_values.append(ema)
            return {"success": True, "symbol": symbol, "period": period, "ema": ema_values, "current_ema": ema_values[-1] if ema_values else None}
        return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/indicators/rsi")
async def calculate_rsi(symbol: str, period: int = 14):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo")
        if not hist.empty:
            closes = hist['Close'].tolist()
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
            if avg_losses == 0:
                rs = 100
            else:
                rs = avg_gains / avg_losses
                rs = 100 - (100 / (1 + rs))
            rsi_values = []
            for delta in deltas:
                if delta > 0:
                    avg_gains = ((avg_gains * (period - 1)) + delta) / period
                else:
                    avg_losses = ((avg_losses * (period - 1)) + abs(delta)) / period
                if avg_losses == 0:
                    rs = 100
                else:
                    rs = avg_gains / avg_losses
                    rs = 100 - (100 / (1 + rs))
                rsi_values.append(rs)
            return {"success": True, "symbol": symbol, "period": period, "rsi": rsi_values, "current_rsi": rsi_values[-1] if rsi_values else None}
        return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 NTDF API v2.0.0 Starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
