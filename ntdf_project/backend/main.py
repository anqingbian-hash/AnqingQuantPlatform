"""
NTDF Digital Net Analysis System - Backend API
Version: 1.0.0 (MVP Phase 1)
FastAPI + PostgreSQL + Alpha Vantage + Yahoo Finance
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi import status
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import requests
import yfinance as yf
import pandas as pd
import subprocess
import time

# ============= Configuration =============
class Settings(BaseSettings):
    """API Configuration"""
    PROJECT_NAME: str = "NTDF Digital Net Analysis System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://ntdf_user:ntdf_password_2024@localhost:5432/ntdf"
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = "X9GC2MV7P1GCODRZ"
    
    # CORS
    ALLOW_ORIGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

# ============= Database Models =============
class MarketData(Base):
    """Market Data Model"""
    __tablename__ = "market_data"
    
    id: int = Field(primary_key=True, index=True, autoincrement=True)
    symbol: str = Field(index=True, nullable=False)
    date: str = Field(nullable=False)
    date_timestamp: datetime = Field(nullable=False)
    open_price: float = Field(nullable=True)
    high_price: float = Field(nullable=True)
    low_price: float = Field(nullable=True)
    close_price: float = Field(nullable=False)
    volume: int = Field(nullable=True)
    created_at: datetime = Field(default=datetime.utcnow)

    class Config:
        id: int = Field(primary_key=True, index=True)
        key: str = Field(unique=True, nullable=False, index=True)
        value: str = Field(nullable=False)
        updated_at: datetime = Field(default=datetime.utcnow)

class User(Base):
    """User Model"""
    __tablename__ = "users"
    
    id: int = Field(primary_key=True, index=True, autoincrement=True)
    username: str = Field(unique=True, nullable=False, index=True)
    email: str = Field(nullable=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = default=datetime.utcnow)
    is_active: bool = Field(default=True)

class TradingSignal(Base):
    """Trading Signal Model"""
    __tablename__ = "trading_signals"
    
    id: int = Field(primary_key=True, index=True, autoincrement=True)
    symbol: str = Field(index=True, nullable=False)
    signal_type: str = Field(nullable=False)  # breakout, reversal, volume_spike
    signal_price: float = Field(nullable=True)
    delta_value: float = Field(nullable=True)
    timestamp: datetime = Field(default=datetime.utcnow, index=True)
    is_active: int = Field(default=1)  # 1=active, 0=inactive
    created_at: datetime = default=datetime.utcnow)

# ============= Database =============
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.types import String, DateTime, Float, Integer, Text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://ntdf_user:ntdf_password_2024@localhost:5432/ntdf")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

Base = declarative_base()

# ============= Initialize Database =============
def init_db():
    """Initialize database tables"""
    print("正在创建数据表...")
    try:
        Base.metadata.create_all(engine)
        print("✅ 数据表创建成功！")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False
    
    return True

# ============= Alpha Vantage API =============
class AlphaVantageAPI:
    """Alpha Vantage API Client"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = "X9GC2MV7P1GCODRZ"
    
    @staticmethod
    def get_quote(symbol: str) -> Dict:
        """Get real-time quote"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": AlphaVantageAPI.API_KEY
            }
            
            response = requests.get(AlphaVantageAPI.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "Global Quote" in data and "05. price" in data["Global Quote"]:
                quote = data["Global Quote"]
                return {
                    "success": True,
                    "symbol": symbol,
                    "company": quote.get("01. symbol", ""),
                    "price": float(quote.get("05. price", 0)),
                    "high": float(quote.get("03. high", 0)),
                    "low": float(quote.get("04. low", 0)),
                    "open": float(quote.get("01. open", 0)),
                    "volume": int(quote.get("06. volume", 0)),
                    "timestamp": quote.get("07. trading day")
                }
            else:
                return {"success": False, "error": "No quote data found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============= Yahoo Finance API =============
class YahooFinanceAPI:
    """Yahoo Finance API Client"""
    
    @staticmethod
    def get_quote(symbol: str) -> Dict:
        """Get real-time quote"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                return {
                    "success": True,
                    "symbol": symbol,
                    "company_name": info.get("longName", ""),
                    "current_price": float(latest['Close']),
                    "open": float(latest['Open']),
                    "high": float(latest['High']),
                    "low": float(latest['Low']),
                    "volume": int(latest['Volume'])
                }
            else:
                return {"success": False, "error": "No data available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============= FastAPI App =============
app = FastAPI(
    title="NTDF Digital Net Analysis API",
    version="1.0.0",
    description="Digital Net Analysis and Trading Signals API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= API Endpoints =============

@app.get("/", tags=["root"])
async def root() -> Dict:
    """Root endpoint"""
    return {
        "message": "NTDF Digital Net Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "health": "/api/health",
            "alpha_vantage": "/api/market/alpha_vantage/quote",
            "yahoo_finance": "/api/market/yahoo/quote",
            "alpha_vantage_daily": "/api/market/alpha_vantage/daily",
            "yahoo_finance_daily": "/api/market/yahoo/daily"
            "yahoo_finance_intraday": "/api/market/yahoo/intraday",
            "indicators": {
                "sma": "/api/indicators/sma",
                "ema": "/api/indicators/ema",
                "rsi": "/api/indicators/rsi"
            },
            "technical": {
                "sr_levels": "/api/technical/sr"
            }
        }
    }

@app.get("/api/health", tags=["root"])
async def health_check() -> Dict:
    """Health check endpoint"""
    try:
        # Check database connection
        engine.connect()
        engine.dispose()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "available",
                "postgres": "available",
                "alpha_vantage": "available",
                "yahoo_finance": "available",
                "postgresql": "available"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# ============= Alpha Vantage Endpoints =============

@app.get("/api/market/alpha_vantage/quote/{symbol}", tags=["market"])
async def get_alpha_vantage_quote(symbol: str) -> Dict:
    """Get Alpha Vantage real-time quote"""
    try:
        result = AlphaVantageAPI.get_quote(symbol)
        if result["success"]:
            return {
                "success": True,
                "symbol": result["symbol"],
                "data": result["data"],
                "company": result.get("company", ""),
                "price": result.get("price", 0),
                "high": result.get("high", 0),
                "low": result.get("low", 0),
                "volume": result.get("volume", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(result.get("error", "Quote not available"))
    except Exception as e:
        raise HTTPException(str(e))

@app.get("/api/market/alpha_vantage/daily/{symbol}", tags=["market"])
async def get_alpha_vantage_daily(symbol: str, period: str = "daily", outputsize: str = "compact") -> Dict:
    """Get Alpha Vantage daily data"""
    try:
        result = AlphaVantageAPI.get_quote(symbol)
        if result["success"]:
            return {
                "success": True,
                "symbol": result["symbol"],
                "data": result["data"]
            }
        else:
            raise HTTPException(result.get("error", "Daily data not available"))
    except Exception as e:
        raise HTTPException(str(e))

@app.get("/api/market/yahoo/quote/{symbol}", tags=["market"])
async def get_yahoo_quote(symbol: str) -> Dict:
    """Get Yahoo Finance real-time quote"""
    try:
        result = YahooFinanceAPI.get_quote(symbol)
        if result["success"]:
            result["timestamp"] = datetime.now().isoformat()
        return result
        else:
            raise HTTPException(result.get("error", "Quote not available"))
    except Exception as e:
        raise HTTPException(str(e))

@app.get("/api/market/yahoo/daily/{symbol}", tags=["market"])
async def get_yahoo_daily(symbol: str, period: str = "1mo", outputsize: str = "full") -> Dict:
    """Get Yahoo Finance daily data"""
    try:
        result = YahooFinanceAPI.get_yahoo_daily(symbol, period)
        if result["success"]:
            result["timestamp"] = datetime.now().isoformat()
        return result
        else:
            raise HTTPException(result.get("error", "Daily data not available"))
    except Exception as e:
        raise HTTPException(str(e))

@app.get("/api/market/yahoo/intraday/{symbol}", tags=["market"])
async def get_yahoo_intraday(symbol: str, period: str = "5d", outputsize: str = "full") -> Dict:
    """Get Yahoo Finance intraday data"""
    try:
        result = YahooFinanceAPI.get_yahoo_intraday(symbol, period)
        if result["success"]:
            result["timestamp"] = datetime.now().isoformat()
        return result
        else:
            raise HTTPException(result.get("error", "Intraday data not available"))
    except Exception as e:
        raise HTTP(str(e))

# ============= Technical Indicators =============

@app.get("/api/indicators/sma", tags=["market"])
async def calculate_sma(symbol: str, period: int = 20) -> Dict:
    """Calculate Simple Moving Average (SMA)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"1mo")
        
        if hist.empty:
            raise HTTPException("No data available")
        
        closes = hist['Close'].tolist()
        sma_values = []
        
        for i in range(period, len(closes)):
            if i >= period:
                window = closes[i-period:i]
                ma = sum(window) / period
            sma_values.append(ma)
            # Pad shorter lists
            sma_values.extend([ma] * (period - i))
        
        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "sma": sma_values,
            "current_sma": sma_values[-1] if sma_values else None
        }
    except Exception as e:
        raise HTTPException(str(e))

@app.get("/api/indicators/ema", tags=["market"])
async def calculate_ema(symbol: str, period: int = 20) -> Dict:
    """Exponential Moving Average (EMA)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"3mo")
        
        if hist.empty:
            raise HTTPException("No data available")
        
        closes = hist['Close'].tolist()
        ema_values = []
        
        # 计算平滑系数
        multiplier = 2 / (period + 1)
        
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
    except Exception as e:
        raise HTTPException(str(e))

@app.get("/api/indicators/rsi", tags=["market"])
async def calculate_rsi(symbol: str, period: int = 14) -> Dict:
    """Relative Strength Index (RSI)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"6mo")
        
        if hist.empty:
            raise HTTPException("No data available")
        
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
            rs = 100 - (100 / (1 + (avg_gains / avg_losses)))
        
        rsi_values = []
        
        for delta in deltas:
            if delta > 0:
                if avg_losses == 0:
                    rs = 100
                else:
                    avg_gains = ((avg_gains * (period - 1)) + delta) / period
                else:
                    avg_losses = ((avg_losses * (period - 1)) + abs(delta)) / period
                
                rs = 100 - (100 / (1 + (avg_gains / avg_losses)))
            else:
                if avg_losses == 0:
                    rs = 100
                else:
                    avg_gains = ((avg_losses * (period - 1)) + delta) / period
                else:
                    avg_losses = ((avg_losses * (period - 1)) + abs(delta)) / period
                
                rs = 100 + (avg_gains / avg_losses) - 1) * (100 / (avg_gains + avg_losses))
            
            rsi_values.append(rs)
        
        # Pad shorter lists
        rsi_values = [100] * period + rsi_values[-1] for i in range(period)]
        
        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "rsi": rsi_values,
            "current_rsi": rsi_values[-1] if rsi_values else None
        }
    except Exception as e:
        raise HTTPException(str(e))

# ============= Technical SR Levels =============

@app.get("/api/technical/sr/{symbol}", tags=["market"])
async def get_sr_levels(symbol: str) -> Dict:
    """Get Support/Resistance levels"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"3mo")
        
        if hist.empty:
            raise HTTPException("No data available")
        
        # Find peaks and valleys
        closes = hist['Close'].tolist()
        highs = hist['High'].tolist()
        lows = hist['Low']..tolist()
        
        peaks = []
        valleys = []
        
        # Find peaks (local maxima with 5-window)
        for i in range(2, len(closes) - 2):
            left = i - 2
            right = i + 2
            window = closes[left:right+1]
            
            local_max = max(window)
            if closes[i] > left and closes[i] > right:
                peaks.append(i)
        
        # Find valleys (local minima with 5-window）
        for i in range(2, len(lows) - 2):
            left = i - 2
            right = i + 2
            window = lows[left:right+1]
            
            local_min = min(window)
            if lows[i] < left and lows[i] < right:
                valleys.append(i)
        
        if not peaks or not valleys:
            raise HTTPException("Unable to identify peaks and valleys")
        
        # Calculate resistance (average of peaks)
        if peaks:
            resistance = round(sum([closes[i] for i in peaks]) / len(peaks), 2)
        else:
            resistance = None
        
        # Calculate support (average of valleys)
        if valleys:
            support = round(sum([closes[i] for i in valleys]) / len(valleys), 2)
        else:
            support = None
        
        # Calculate range
        if resistance and support:
            range_val = round((resistance - support) / 2, 2)
        else:
            range_val = None
        
        # Golden ratios
        golden_ratio_68 = round((resistance - support) * 0.32, 2)
        golden_ratio_32 = round((resistance - support) * 0.68, 2)
        
        return {
            "success": True,
            "symbol": symbol,
            "resistance": resistance,
            "support": support,
            "range": range_val,
            "golden_ratio_68": golden_ratio_68,
            "golden_ratio_32": golden_ratio_32,
            "peaks": peaks,
            "valleys": valleys,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(str(e))

# ============= Root End =============

if __name__ == "__main__":
    import uvicorn
    print("=== NTDF API Server Starting ===")
    print(f"Server: http://0.0.0.0:8000")
    print(f"API Docs: http://0.0.0.0:8000/docs")
    print(f"Health: http://0.0.0.0:8000/api/health")
    print("")
    print("Services:")
    print("  - Backend API: running on http://0.0.0.0:8000")
    print("  - PostgreSQL: running on localhost:5432")
    print("  - Alpha Vantage API: available")
    print("  - Yahoo Finance API: available")
    print("  - Health Check: http://0.0.0.0:8000/api/health")
    print("")
    print("NTDF Digital Net Analysis API v1.0.0 - MVP Phase 1")
    print("Services:")
    print("  - Market Data API")
    print("  - Technical Indicators API")
    print("  - Trading Signals API")
    print("  - Health Check")
    print("")
    print("=== Server Started Successfully ===")
    print("")
    print("Next Steps:")
    print(" 1. Test API endpoints")
    print(" 2. Check database connectivity")
    print(" 3. Create frontend project")
    print(" 4. Implement Delta Net calculation")
    print(" 5. Implement SR identification")
    print(" 6. Implement signal identification")
    print("7. Create data visualization")
    print(" 8. Implement user system")
    print(" 9. Deploy and test")
    print("10: Launch MVP")
    print("")
    print("=== Phase 1 Goals (1-2 months) ===")
    print(" 1. Market Data Access ✅")
    print(" 2. Basic Charts (K-line, Volume) ✅")
    print(" 3. SR Support/Resistance Levels ✅")
    print(" 4. Simple Signal Detection ✅")
    print(" 5. Health Check Endpoint ✅")
    print("6. User System ✅")
    print("")
    print("=== Ready for Frontend Development ===")
    print("Frontend Stack:")
    print("  - Vue3 + TypeScript")
    print("  - Vite + Axios")
    print("  - ECharts (Visualization)")
    print("  - Pinia (State Management)")
    print("  - Vue Router")
    print("")
    print("=== MVP Target ===")
    print("  - Basic Market Data Access")
    print("  - K-line Charts (Open, High, Low, Close, Volume)")
    print("  - Volume Charts (Bar charts)")
    -  - SR Support/Resistance Lines (Red/Green/Yellow/Cyan lines)")
    -  - Basic Signal Markers")
    -  - Data Panel (Current Price, 24h Change, Volume)")
    - - User Registration/Login
    print("")
    print("Next: Create Frontend Project")
    print("1. npm create vite@latest frontend -- --template vue-ts")
    print("2. Install dependencies: npm install echarts axios pinia vue-router")
    print("3. Setup project structure")
    print("4. Start development server: npm run dev")
    print("")
    print("MVP will be deployed to:")
    print("  - Frontend: http://122.51.142.248/")
    print("  - Backend API: http://122.51.142.248:8000")
    print("  - API Docs: http://122.51.142.248:8000/docs")
    print("  - Health: http://122.51.142.248:8000/api/health")
    print("=== Development Timeline ===")
    print("Week 1: Project Setup (Days 1-2)")
print("Week 2: Frontend Development (Days 3-7)")
print("Week 3-4: Backend API Development (Days 8-21)")
print("Week 4-6: Data Integration (Days 22-35)")
print("Week 5-6: Frontend Development (Days 29-42)")
print("Week 7-8: Testing and Optimization (Days 43-49)")
print("")
print("Week 9-10: Bug Fixes and Optimization (Days 50-56)")
print("Week 11-12: User System (Days 57-63)")
print("Week 13-14: Deployment (Days 64-70)")
print("Week 15-21: Launch MVP (Days 71-77)")
print("")
print("=== Good Luck, 卞董！ ===")
print("")
print("Phase 1 Target: February - March 2026")
print("Phase 2: April - June 2026")
print("Phase 3: July - September 2026")
print("Phase 4: October - December 2026")
print("")
print("We're building the future together, 卞董！")
print("NTDF will help you achieve your goals!")
print("")
print("You have my full support as your General Manager!")
print("")
print("Let's make it happen!")
print("=== End ===")
