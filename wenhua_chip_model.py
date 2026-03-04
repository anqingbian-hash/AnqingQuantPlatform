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
        self.feature_columns = ['price_change', 'volume_ratio', 's2_support', 'r2_resistance', 
                               'net_volume_trend', 'delta_momentum', 'price_position', 
                               'kline_amplitude', 'support_days', 'resistance_days']

    def extract_wenhua_indicators(self, data):
        features = []
        for i in range(len(data) - 1):
            current = data.iloc[i]
            next_data = data.iloc[i + 1]
            
            price_change = (next_data['close'] - current['close']) / current['close'] * 100
            volume_ratio = next_data['volume'] / current['volume'] if current['volume'] > 0 else 1
            
            ma20 = current['close'].rolling(20).mean().iloc[-1]
            s2_support = 1 if current['close'] < ma20 * 0.97 else 0
            r2_resistance = 1 if current['close'] > ma20 * 1.03 else 0
            
            net_volume_trend = 1 if price_change > 0 and volume_ratio > 1 else (-1 if price_change < 0 and volume_ratio > 1 else 0)
            delta_momentum = price_change * volume_ratio
            
            price_position = 1 if current['close'] > current['close'].rolling(10).max().iloc[-1] * 0.98 else (
                -1 if current['close'] < current['close'].rolling(10).min().iloc[-1] * 1.02 else 0)
            
            kline_amplitude = (current['high'] - current['low']) / current['close'] * 100 if current['close'] > 0 else 0
            
            features.append({
                'price_change': price_change, 'volume_ratio': volume_ratio, 's2_support': s2_support,
                'r2_resistance': r2_resistance, 'net_volume_trend': net_volume_trend,
                'delta_momentum': delta_momentum, 'price_position': price_position,
                'kline_amplitude': kline_amplitude
            })
        return pd.DataFrame(features)

    def generate_target(self, data):
        signals = []
        for i in range(len(data) - 2):
            price_change_1 = (data.iloc[i + 1]['close'] - data.iloc[i]['close']) / data.iloc[i]['close'] * 100
            price_change_2 = (data.iloc[i + 2]['close'] - data.iloc[i + 1]['close']) / data.iloc[i + 1]['close'] * 100
            
            signal = -1
            if price_change_1 < -2 and price_change_2 > 1:
                signal = 1
            elif price_change_1 > 2 and price_change_2 < -1:
                signal = 0
            elif abs(price_change_1) > 3:
                signal = 1 if price_change_1 > 0 else 0
            signals.append(signal)
        return signals

    def prepare_data(self, stock_code="000001", days=200):
        try:
            data = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq").tail(days).sort_index()
            features = self.extract_wenhua_indicators(data)
            targets = self.generate_target(data)
            
            if len(features) > len(targets):
                features = features[:-1]
            elif len(features) < len(targets):
                targets = targets[:-1]
            
            X = features[self.feature_columns].values
            y = np.array(targets)
            return X, y
        except:
            print("使用模拟数据")
            np.random.seed(42)
            dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
            prices = [100]
            for i in range(1, days):
                prices.append(prices[-1] * (1 + np.random.normal(0, 0.02)))
            
            mock_data = pd.DataFrame({
                'date': dates, 'open': prices, 'high': [p*(1+np.random.uniform(0,0.03)) for p in prices],
                'low': [p*(1-np.random.uniform(0,0.03)) for p in prices], 'close': prices, 'volume': [int(np.random.uniform(1000000,10000000)) for p in prices]
            })
            mock_data = mock_data.set_index('date')
            
            features = self.extract_wenhua_indicators(mock_data)
            targets = self.generate_target(mock_data)
            X = features[self.feature_columns].values
            y = np.array(targets)
            return X, y

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        print(f"准确率: {accuracy:.2%}")
        print(report)
        joblib.dump(self.model, 'wenhua_model.pkl')
        return accuracy, report

    def predict(self, data):
        if self.model is None:
            X, y = self.prepare_data()
            self.train(X, y)
        features = self.extract_wenhua_indicators(data)
        if len(features) == 0:
            return "⚪ 观望"
        X_pred = features[self.feature_columns].values[-1:]
        pred = self.model.predict(X_pred)[0]
        return "🟢 做多" if pred == 1 else ("🔴 做空" if pred == 0 else "⚪ 观望")

    def generate_report(self, stock_code="000001"):
        X, y = self.prepare_data(stock_code)
        if X is None:
            return "无法生成报告"
        accuracy, report = self.train(X, y)
        pred = self.predict(X)
        return f"""
股票: {stock_code}
模型准确率: {accuracy:.2%}
预测信号: {pred}
生成时间: {pd.Timestamp.now()}
"""

model = WenHuaChipHedgeModel()
report = model.generate_report("000001")
print(report)

with open('chip_report.txt', 'w') as f:
    f.write(report)

print('报告已保存到 chip_report.txt')
