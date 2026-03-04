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

    def create_mock_data(self, days=100):
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
        base_price = 100
        prices = [base_price]
        volumes = [int(np.random.uniform(1000000, 10000000))]
        
        for i in range(1, days):
            change = np.random.normal(0, 0.02)
            prices.append(prices[-1] * (1 + change))
            volumes.append(int(np.random.uniform(1000000, 10000000)))
        
        mock_data = pd.DataFrame({
            'close': prices,
            'volume': volumes
        })
        return mock_data

    def extract_features(self, data):
        features = []
        close_prices = data['close'].values
        volumes = data['volume'].values
        
        for i in range(len(data) - 1):
            prev_close = close_prices[i]
            close = close_prices[i + 1]
            volume = volumes[i + 1]
            prev_volume = volumes[i]
            
            # 价格变化和成交量比率
            price_change = (close - prev_close) / prev_close * 100 if prev_close > 0 else 0
            volume_ratio = volume / prev_volume if prev_volume > 0 else 1
            
            # 简化的支撑阻力判断
            ma20 = np.mean(close_prices[max(0, i - 19):i + 1]) if i >= 19 else prev_close
            ma_support = 1 if prev_close < ma20 * 0.97 else 0
            ma_resistance = 1 if prev_close > ma20 * 1.03 else 0
            
            # 净量趋势和Delta动量
            net_volume_trend = 1 if price_change > 0 and volume_ratio > 1 else (-1 if price_change < 0 and volume_ratio > 1 else 0)
            delta_momentum = price_change * volume_ratio
            
            # 价格位置
            price_position = 0
            if i > 0:
                recent_high = np.max(close_prices[max(0, i - 9):i + 1])
                recent_low = np.min(close_prices[max(0, i - 9):i + 1])
                if prev_close > recent_high * 0.98:
                    price_position = 1
                elif prev_close < recent_low * 1.02:
                    price_position = -1
            
            # K线振幅
            kline_amp = (close_prices[i] - close_prices[i - 1]) / close_prices[i] * 100 if i > 0 and close_prices[i] > 0 else 0
            
            features.append({
                'price_change': price_change,
                'volume_ratio': volume_ratio,
                'ma_support': ma_support,
                'ma_resistance': ma_resistance,
                'net_volume_trend': net_volume_trend,
                'delta_momentum': delta_momentum,
                'price_position': price_position,
                'kline_amp': kline_amp
            })
        return pd.DataFrame(features)

    def generate_targets(self, data):
        signals = []
        close_prices = data['close'].values
        
        for i in range(len(data) - 2):
            price_change_1 = (close_prices[i + 1] - close_prices[i]) / close_prices[i] * 100 if close_prices[i] > 0 else 0
            price_change_2 = (close_prices[i + 2] - close_prices[i + 1]) / close_prices[i + 1] * 100 if close_prices[i + 1] > 0 else 0
            
            signal = -1  # 观望
            if price_change_1 < -2 and price_change_2 > 1:
                signal = 1  # 做多
            elif price_change_1 > 2 and price_change_2 < -1:
                signal = 0  # 做空
            elif abs(price_change_1) > 3:
                signal = 1 if price_change_1 > 0 else 0
            
            signals.append(signal)
        return signals

    def prepare_data(self, stock_code="000001", days=100):
        try:
            stock_data = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq").tail(days).sort_index()
            if stock_data is None or len(stock_data) < days:
                print('使用模拟数据')
                mock_data = self.create_mock_data(days)
                features = self.extract_features(mock_data)
                targets = self.generate_targets(mock_data)
                X = features.values
                y = np.array(targets)
                return X, y
            
            features = self.extract_features(stock_data)
            targets = self.generate_targets(stock_data)
            if len(features) > len(targets):
                features = features[:-1]
            elif len(features) < len(targets):
                targets = targets[:-1]
            
            X = features.values
            y = np.array(targets)
            return X, y
        except:
            print('使用模拟数据')
            mock_data = self.create_mock_data(days)
            features = self.extract_features(mock_data)
            targets = self.generate_targets(mock_data)
            X = features.values
            y = np.array(targets)
            return X, y

    def train_model(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        print(f'模型准确率: {accuracy:.2%}')
        print(report)
        joblib.dump(self.model, 'wenhua_model.pkl')
        return accuracy, report

    def predict(self, data):
        if self.model is None:
            X, y = self.prepare_data()
            self.train_model(X, y)
        features = self.extract_features(data)
        if len(features) == 0:
            return '⚪ 观望'
        X_pred = features.values[-1:]
        p = self.model.predict(X_pred)[0]
        return '🟢 做多' if p == 1 else ('🔴 做空' if p == 0 else '⚪ 观望')

    def report(self, stock_code='000001'):
        X, y = self.prepare_data(stock_code)
        if X is None:
            return '无数据'
        acc, rep = self.train_model(X, y)
        sig = self.predict(X)
        return f"股票: {stock_code}\n模型准确率: {acc:.2%}\n预测信号: {sig}\n时间: {pd.Timestamp.now()}"

# 执行
model = WenHuaChipHedgeModel()
print(model.report('000001'))

with open('chip_report.txt', 'w') as f:
    f.write(model.report('000001'))

print('报告已保存到 chip_report.txt')
