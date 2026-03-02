"""
NTDF Digital Net Analysis System - Backend API
Version: 2.2.0 (ZhuLinsen-Hybrid Edition)
FastAPI + PostgreSQL + Alpha Vantage + Yahoo Finance + yfinance + pandas + numpy + requests
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import yfinance as yf
import pandas as pd
import numpy as np

# ==================== Configuration ====================
class Settings:
    PROJECT_NAME: str = "NTDF Digital Net Analysis System"
    VERSION: str = "2.2.0 (ZhuLinsen-Hybrid)"
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

settings = Settings()

# ==================== FastAPI App ====================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="NTDF Digital Net Analysis System - ZhuLinsen Hybrid Edition"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# ==================== Database Models ====================
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as DBSession

Base = declarative_base()

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(20), index=True, nullable=False)
    date = Column(String(20), nullable=False)
    date_timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class TradingSignal(Base):
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(20), index=True, nullable=False)
    signal_type = Column(String(20), nullable=False)  # breakout, reversal, volume_spike
    signal_price = Column(Float, nullable=True)
    delta_value = Column(Float, nullable=True)
    sr_high = Column(Float, nullable=True)
    sr_low = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    is_active = Column(Boolean, default=True)  # True=active, False=inactive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)  # True=active, False=inactive

# ==================== Database Engine ====================
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==================== Pydantic Models ====================
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class QuoteResponse(BaseModel):
    success: bool
    symbol: str
    company_name: Optional[str] = None
    current_price: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    volume: Optional[int] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

class DailyDataResponse(BaseModel):
    success: bool
    symbol: str
    interval: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SMARequest(BaseModel):
    symbol: str
    period: int = 20

class EMASRequest(BaseModel):
    symbol: str
    period: int = 20

class RSIRequest(BaseModel):
    symbol: str
    period: int = 14

class IndicatorResponse(BaseModel):
    success: bool
    symbol: str
    period: int
    data: Optional[List[float]] = None
    current_value: Optional[float] = None
    error: Optional[str] = None

# ==================== Utility Functions ====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== Basic Endpoints ====================
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.VERSION
    )

@app.get("/")
async def root():
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }

# ==================== Alpha Vantage Endpoints ====================
@app.get("/api/v1/market/alpha_vantage/quote", response_model=QuoteResponse)
async def get_alpha_vantage_quote(symbol: str):
    """Get real-time quote from Alpha Vantage"""
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY
        }
        response = requests.get("https://www.alphavantage.co/query", params=params, timeout=10)
        data = response.json()
        
        if "Global Quote" in data:
            quote = data["Global Quote"]
            return QuoteResponse(
                success=True,
                symbol=symbol,
                company_name=quote.get("01. symbol", ""),
                current_price=float(quote.get("05. price", 0)),
                high=float(quote.get("03. high", 0)),
                low=float(quote.get("04. low", 0)),
                open=float(quote.get("02. open", 0)),
                volume=int(quote.get("06. volume", 0)),
                timestamp=quote.get("07. latest trading day", "")
            )
        
        return QuoteResponse(
            success=False,
            symbol=symbol,
            error="No data available"
        )
    except Exception as e:
        return QuoteResponse(
            success=False,
            symbol=symbol,
            error=str(e)
        )

@app.get("/api/v1/market/alpha_vantage/daily", response_model=DailyDataResponse)
async def get_alpha_vantage_daily(symbol: str, outputsize: str = "compact"):
    """Get daily data from Alpha Vantage"""
    try:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
            "outputsize": outputsize
        }
        response = requests.get("https://www.alphavantage.co/query", params=params, timeout=10)
        data = response.json()
        
        if "Time Series (Daily)" in data:
            return DailyDataResponse(
                success=True,
                symbol=symbol,
                interval="daily",
                data=data["Time Series (Daily)"]
            )
        
        return DailyDataResponse(
            success=False,
            symbol=symbol,
            error="No time series data available"
        )
    except Exception as e:
        return DailyDataResponse(
            success=False,
            symbol=symbol,
            error=str(e)
        )

# ==================== Yahoo Finance Endpoints ====================
@app.get("/api/v1/market/yahoo/quote", response_model=QuoteResponse)
async def get_yahoo_quote(symbol: str):
    """Get real-time quote from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            latest = hist.iloc[-1]
            return QuoteResponse(
                success=True,
                symbol=symbol,
                current_price=float(latest['Close']),
                high=float(latest['High']),
                low=float(latest['Low']),
                open=float(latest['Open']),
                volume=int(latest['Volume']),
                timestamp=datetime.now().isoformat()
            )
        
        return QuoteResponse(
            success=False,
            symbol=symbol,
            error="No data available"
        )
    except Exception as e:
        return QuoteResponse(
            success=False,
            symbol=symbol,
            error=str(e)
        )

@app.get("/api/v1/market/yahoo/daily", response_model=DailyDataResponse)
async def get_yahoo_daily(symbol: str):
    """Get daily data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        
        if not hist.empty:
            data = {}
            for date, row in hist.iterrows():
                data[date.strftime("%Y-%m-%d")] = {
                    "1. open": float(row['Open']),
                    "2. high": float(row['High']),
                    "3. low": float(row['Low']),
                    "4. close": float(row['Close']),
                    "5. volume": int(row['Volume'])
                }
            
            return DailyDataResponse(
                success=True,
                symbol=symbol,
                interval="daily",
                data=data
            )
        
        return DailyDataResponse(
            success=False,
            symbol=symbol,
            error="No time series data available"
        )
    except Exception as e:
        return DailyDataResponse(
            success=False,
            symbol=symbol,
            error=str(e)
        )

# ==================== Technical Indicators Endpoints ====================
@app.post("/api/v1/indicators/sma", response_model=IndicatorResponse)
async def calculate_sma(request: SMARequest):
    """Calculate Simple Moving Average (SMA)"""
    try:
        ticker = yf.Ticker(request.symbol)
        hist = ticker.history(period="3mo")
        
        if not hist.empty:
            closes = hist['Close'].tolist()
            sma_values = []
            
            for i in range(len(closes)):
                if i >= request.period:
                    window = closes[i-request.period:i]
                    ma = sum(window) / request.period
                else:
                    ma = None
                sma_values.append(ma)
            
            return IndicatorResponse(
                success=True,
                symbol=request.symbol,
                period=request.period,
                data=sma_values,
                current_value=sma_values[-1] if sma_values else None
            )
        
        return IndicatorResponse(
            success=False,
            symbol=request.symbol,
            period=request.period,
            error="No data available"
        )
    except Exception as e:
        return IndicatorResponse(
            success=False,
            symbol=request.symbol,
            period=request.period,
            error=str(e)
        )

@app.post("/api/v1/indicators/ema", response_model=IndicatorResponse)
async def calculate_ema(request: EMASRequest):
    """Calculate Exponential Moving Average (EMA)"""
    try:
        ticker = yf.Ticker(request.symbol)
        hist = ticker.history(period="3mo")
        
        if not hist.empty:
            closes = hist['Close'].tolist()
            multiplier = 2 / (request.period + 1)
            ema_values = []
            ema = closes[0]
            ema_values.append(ema)
            
            for price in closes[1:]:
                ema = (price - ema) * multiplier + ema
                ema_values.append(ema)
            
            return IndicatorResponse(
                success=True,
                symbol=request.symbol,
                period=request.period,
                data=ema_values,
                current_value=ema_values[-1] if ema_values else None
            )
        
        return IndicatorResponse(
            success=False,
            symbol=request.symbol,
            period=request.period,
            error="No data available"
        )
    except Exception as e:
        return IndicatorResponse(
            success=False,
            symbol=request.symbol,
            period=request.period,
            error=str(e)
        )

@app.post("/api/v1/indicators/rsi", response_model=IndicatorResponse)
async def calculate_rsi(request: RSIRequest):
    """Calculate Relative Strength Index (RSI)"""
    try:
        ticker = yf.Ticker(request.symbol)
        hist = ticker.history(period="6mo")
        
        if not hist.empty:
            closes = hist['Close'].tolist()
            deltas = []
            
            for i in range(1, len(closes)):
                deltas.append(closes[i] - closes[i-1])
            
            # Calculate initial average gains/losses
            initial_gains = [max(delta, 0) for delta in deltas[:request.period]]
            initial_losses = [abs(min(delta, 0)) for delta in deltas[:request.period]]
            
            avg_gain = sum(initial_gains) / request.period
            avg_loss = sum(initial_losses) / request.period
            
            rsi_values = []
            
            # Calculate RSI for each period
            for i in range(request.period, len(deltas)):
                # Update averages using Wilder's smoothing
                delta = deltas[i]
                gain = max(delta, 0)
                loss = abs(min(delta, 0))
                
                avg_gain = ((avg_gain * (request.period - 1)) + gain) / request.period
                avg_loss = ((avg_loss * (request.period - 1)) + loss) / request.period
                
                if avg_loss == 0:
                    rs = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                rsi_values.append(rsi)
            
            return IndicatorResponse(
                success=True,
                symbol=request.symbol,
                period=request.period,
                data=rsi_values,
                current_value=rsi_values[-1] if rsi_values else None
            )
        
        return IndicatorResponse(
            success=False,
            symbol=request.symbol,
            period=request.period,
            error="No data available"
        )
    except Exception as e:
        return IndicatorResponse(
            success=False,
            symbol=request.symbol,
            period=request.period,
            error=str(e)
        )

# ==================== Main Entry Point ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
