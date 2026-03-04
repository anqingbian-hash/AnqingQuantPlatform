import akshare as ak
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class WenHuaChipHedgeModel:
    def __init__(self):
        self.model = None
        self.feature_columns = ['price_change', 'volume_ratio', 'ma_support', 'ma_resistance', 
                               'net_volume_trend', 'delta_momentum', 'price_position', 'kline_amp']

    def extract_features(self, data):
        features = []
        for i in range(len(data) - 1):
            current = data.iloc[i]
            next_row = data.iloc[i + 1]
            
            # 价格和成交量
            prev_close = current['close']
            close = next_row['close']
            volume = next_row['volume']
            prev_volume = current['volume']
            
            # 价格变化和成交量比率
            price_change = (close - prev_close) / prev_close * 100 if prev_close > 0 else 0
            volume_ratio = volume / prev_volume if prev_volume > 0 else 1
            
            # 简单支撑阻力(基于收盘价波动)
            ma_support = 1 if prev_close < current['close'].rolling(20).mean().iloc[-1] * 0.97 else 0
            ma_resistance = 1 if prev_close > current['close'].rolling(20).mean().iloc[-1] * 1.03 else 0
            
            # 净量和动量
            net_volume_trend = 1 if price_change > 0 and volume_ratio > 1 else (-1 if price_change < 0 and volume_ratio > 1 else 0)
            delta_momentum = price_change * volume_ratio
            
            # 价格位置
            price_position = 0
            recent_high = current['close'].rolling(10).max().iloc[-1]
            recent_low = current['close'].rolling(10).min().iloc[-1]
            if prev_close > recent_high * 0.98:
                price_position = 1
            elif prev_close < recent_low * 1.02:
                price_position = -1
            
            # K线振幅
            kline_amp = (current['high'] - current['low']) / current['close'] * 100 if current['close'] > 0 else 0
            
            features.append({
                'price_change': price_change, 'volume_ratio': volume_ratio, 'ma_support': ma_support,
                'ma_resistance': ma_resistance, 'net_volume_trend': net_volume_trend,
                'delta_momentum': delta_momentum, 'price_position': price_position, 'kline_amp': kline_amp
            })
        return pd.DataFrame(features)

    def generate_targets(self, data):
        signals = []
        for i in range(len(data) - 2):
            p1 = (data.iloc[i+1]['close'] - data.iloc[i]['close']) / data.iloc[i]['close'] * 100
            p2 = (data.iloc[i+2]['close'] - data.iloc[i+1]['close']) / data.iloc[i+1]['close'] * 100
            signal = -1
            if p1 < -2 and p2 > 1:
                signal = 1
            elif p1 > 2 and p2 < -1:
                signal = 0
            elif abs(p1) > 3:
                signal = 1 if p1 > 0 else 0
            signals.append(signal)
        return signals

    def prepare_data(self, stock_code='000001', days=100):
        try:
            data = ak.stock_zh_a_daily(symbol=stock_code, adjust='qfq').tail(days).sort_index()
            if data is None or len(data) < days:
                print('使用模拟数据')
                return self.mock_data(days)
            features = self.extract_features(data)
            targets = self.generate_targets(data)
            if len(features) > len(targets):
                features = features[:-1]
            elif len(features) < len(targets):
                targets = targets[:-1]
            X = features[self.feature_columns].values
            y = np.array(targets)
            print(f'数据就绪: {X.shape[0]}样本')
            return X, y
        except:
            print('模拟数据')
            return self.mock_data(days)

    def mock_data(self, days):
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
        prices = [100]
        for i in range(1, days):
            prices.append(prices[-1]*(1+np.random.normal(0,0.02)))
        data = pd.DataFrame({'close': prices, 'volume': [int(np.random.uniform(1e6,1e7)) for _ in prices]}, index=dates)
        features = self.extract_features(data)
        targets = self.generate_targets(data)
        X = features[self.feature_columns].values
        y = np.array(targets)
        return X, y

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        rep = classification_report(y_test, y_pred)
        print(f'准确率: {acc:.2%}')
        print(rep)
        joblib.dump(self.model, 'wenhua_model.pkl')
        return acc, rep

    def predict(self, data):
        if self.model is None:
            X, y = self.prepare_data()
            self.train(X, y)
        features = self.extract_features(data)
        if len(features) == 0:
            return '⚪ 观望'
        X_pred = features[self.feature_columns].values[-1:]
        p = self.model.predict(X_pred)[0]
        return '🟢 做多' if p == 1 else ('🔴 做空' if p == 0 else '⚪ 观望')

    def report(self, stock_code='000001'):
        X, y = self.prepare_data(stock_code)
        if X is None:
            return '无数据'
        acc, rep = self.train(X, y)
        sig = self.predict(X)
        return f'''股票: {stock_code}
模型准确率: {acc:.2%}
预测信号: {sig}
生成时间: {pd.Timestamp.now()}'''

model = WenHuaChipHedgeModel()
print(model.report('000001'))

with open('chip_report.txt', 'w') as f:
    f.write(model.report('000001'))

print('报告已保存到 chip_report.txt')
