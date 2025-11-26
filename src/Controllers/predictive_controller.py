"""
Módulo de Análisis Predictivo con Machine Learning
Predice valores futuros y detecta anomalías en simulaciones
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class PredictiveAnalyzer:
    """Analizador predictivo con Machine Learning"""
    
    def __init__(self):
        self.models = {}
        self.scaler = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa los modelos de ML"""
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.preprocessing import StandardScaler
            from sklearn.ensemble import IsolationForest
            
            self.LinearRegression = LinearRegression
            self.StandardScaler = StandardScaler
            self.IsolationForest = IsolationForest
            self.ml_available = True
        except ImportError:
            print("Warning: scikit-learn not installed. ML features disabled.")
            self.ml_available = False
    
    def predict_future_values(self, simulation_data: Dict, steps: int = 10) -> Dict:
        """
        Predice valores futuros basándose en tendencias
        
        Args:
            simulation_data: Datos de la simulación
            steps: Número de pasos futuros a predecir
        
        Returns:
            Dict con predicciones por variable
        """
        if not self.ml_available:
            return self._fallback_prediction(simulation_data, steps)
        
        predictions = {}
        
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                try:
                    time_points = list(var_data['data'].keys())
                    values = list(var_data['data'].values())
                    
                    # Convertir a arrays numpy
                    X = np.array([float(t) for t in time_points]).reshape(-1, 1)
                    y = np.array(values)
                    
                    # Entrenar modelo
                    model = self.LinearRegression()
                    model.fit(X, y)
                    
                    # Predecir valores futuros
                    last_time = float(time_points[-1])
                    future_times = [last_time + i for i in range(1, steps + 1)]
                    future_X = np.array(future_times).reshape(-1, 1)
                    future_values = model.predict(future_X)
                    
                    # Calcular intervalo de confianza (simple)
                    residuals = y - model.predict(X)
                    std_error = np.std(residuals)
                    confidence_interval = 1.96 * std_error  # 95% CI
                    
                    predictions[var_name] = {
                        'future_times': future_times,
                        'predicted_values': future_values.tolist(),
                        'confidence_lower': (future_values - confidence_interval).tolist(),
                        'confidence_upper': (future_values + confidence_interval).tolist(),
                        'trend': 'increasing' if model.coef_[0] > 0 else 'decreasing',
                        'slope': float(model.coef_[0]),
                        'r2_score': float(model.score(X, y))
                    }
                except Exception as e:
                    print(f"Error predicting {var_name}: {e}")
                    continue
        
        return {
            'success': True,
            'predictions': predictions,
            'steps': steps,
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_anomalies(self, simulation_data: Dict, contamination: float = 0.1) -> Dict:
        """
        Detecta anomalías en los datos de simulación
        
        Args:
            simulation_data: Datos de la simulación
            contamination: Proporción esperada de anomalías (0.1 = 10%)
        
        Returns:
            Dict con anomalías detectadas por variable
        """
        if not self.ml_available:
            return self._fallback_anomaly_detection(simulation_data)
        
        anomalies = {}
        
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                try:
                    values = list(var_data['data'].values())
                    time_points = list(var_data['data'].keys())
                    
                    if len(values) < 10:  # Necesitamos suficientes datos
                        continue
                    
                    # Preparar datos
                    X = np.array(values).reshape(-1, 1)
                    
                    # Detectar anomalías con Isolation Forest
                    clf = self.IsolationForest(contamination=contamination, random_state=42)
                    predictions = clf.fit_predict(X)
                    
                    # Identificar puntos anómalos
                    anomaly_indices = np.where(predictions == -1)[0]
                    anomaly_points = []
                    
                    for idx in anomaly_indices:
                        anomaly_points.append({
                            'time': time_points[idx],
                            'value': values[idx],
                            'severity': self._calculate_severity(values[idx], values)
                        })
                    
                    if anomaly_points:
                        anomalies[var_name] = {
                            'count': len(anomaly_points),
                            'points': anomaly_points,
                            'percentage': (len(anomaly_points) / len(values)) * 100
                        }
                
                except Exception as e:
                    print(f"Error detecting anomalies in {var_name}: {e}")
                    continue
        
        return {
            'success': True,
            'anomalies': anomalies,
            'total_variables_analyzed': len(simulation_data),
            'variables_with_anomalies': len(anomalies),
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_correlations(self, simulation_data: Dict) -> Dict:
        """
        Analiza correlaciones entre variables
        
        Args:
            simulation_data: Datos de la simulación
        
        Returns:
            Dict con matriz de correlación y relaciones significativas
        """
        try:
            # Crear DataFrame con todas las variables
            data_dict = {}
            for var_name, var_data in simulation_data.items():
                if isinstance(var_data, dict) and 'data' in var_data:
                    data_dict[var_name] = list(var_data['data'].values())
            
            df = pd.DataFrame(data_dict)
            
            # Calcular correlaciones
            corr_matrix = df.corr()
            
            # Identificar correlaciones significativas (|r| > 0.7)
            significant_correlations = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        var1 = corr_matrix.columns[i]
                        var2 = corr_matrix.columns[j]
                        significant_correlations.append({
                            'variable1': var1,
                            'variable2': var2,
                            'correlation': float(corr_value),
                            'relationship': 'positive' if corr_value > 0 else 'negative',
                            'strength': self._correlation_strength(abs(corr_value))
                        })
            
            return {
                'success': True,
                'correlation_matrix': corr_matrix.to_dict(),
                'significant_correlations': significant_correlations,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_forecast_report(self, simulation_data: Dict, parameters: Dict) -> Dict:
        """
        Genera reporte completo de pronóstico
        
        Args:
            simulation_data: Datos de la simulación
            parameters: Parámetros utilizados
        
        Returns:
            Dict con reporte completo
        """
        # Predicciones
        predictions = self.predict_future_values(simulation_data, steps=12)
        
        # Anomalías
        anomalies = self.detect_anomalies(simulation_data)
        
        # Correlaciones
        correlations = self.analyze_correlations(simulation_data)
        
        # Estadísticas descriptivas
        statistics = self._calculate_statistics(simulation_data)
        
        return {
            'success': True,
            'predictions': predictions,
            'anomalies': anomalies,
            'correlations': correlations,
            'statistics': statistics,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_severity(self, value: float, all_values: List[float]) -> str:
        """Calcula la severidad de una anomalía"""
        mean = np.mean(all_values)
        std = np.std(all_values)
        z_score = abs((value - mean) / std) if std > 0 else 0
        
        if z_score > 3:
            return 'high'
        elif z_score > 2:
            return 'medium'
        else:
            return 'low'
    
    def _correlation_strength(self, corr: float) -> str:
        """Determina la fuerza de correlación"""
        if corr >= 0.9:
            return 'very strong'
        elif corr >= 0.7:
            return 'strong'
        elif corr >= 0.5:
            return 'moderate'
        else:
            return 'weak'
    
    def _calculate_statistics(self, simulation_data: Dict) -> Dict:
        """Calcula estadísticas descriptivas"""
        stats = {}
        
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                values = list(var_data['data'].values())
                if values:
                    stats[var_name] = {
                        'mean': float(np.mean(values)),
                        'median': float(np.median(values)),
                        'std': float(np.std(values)),
                        'min': float(np.min(values)),
                        'max': float(np.max(values)),
                        'range': float(np.max(values) - np.min(values)),
                        'variance': float(np.var(values))
                    }
        
        return stats
    
    def _fallback_prediction(self, simulation_data: Dict, steps: int) -> Dict:
        """Predicción simple sin sklearn"""
        predictions = {}
        
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                values = list(var_data['data'].values())
                time_points = list(var_data['data'].keys())
                
                if len(values) < 2:
                    continue
                
                # Tendencia lineal simple
                last_value = values[-1]
                prev_value = values[-2]
                trend = last_value - prev_value
                
                future_values = [last_value + trend * i for i in range(1, steps + 1)]
                last_time = float(time_points[-1])
                future_times = [last_time + i for i in range(1, steps + 1)]
                
                predictions[var_name] = {
                    'future_times': future_times,
                    'predicted_values': future_values,
                    'trend': 'increasing' if trend > 0 else 'decreasing',
                    'note': 'Simple linear extrapolation (install scikit-learn for advanced predictions)'
                }
        
        return {
            'success': True,
            'predictions': predictions,
            'steps': steps,
            'is_fallback': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _fallback_anomaly_detection(self, simulation_data: Dict) -> Dict:
        """Detección simple sin sklearn"""
        anomalies = {}
        
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                values = list(var_data['data'].values())
                time_points = list(var_data['data'].keys())
                
                if len(values) < 10:
                    continue
                
                # Método simple: valores fuera de 2 desviaciones estándar
                mean = np.mean(values)
                std = np.std(values)
                threshold = 2 * std
                
                anomaly_points = []
                for i, value in enumerate(values):
                    if abs(value - mean) > threshold:
                        anomaly_points.append({
                            'time': time_points[i],
                            'value': value,
                            'severity': 'medium' if abs(value - mean) > 2.5 * std else 'low'
                        })
                
                if anomaly_points:
                    anomalies[var_name] = {
                        'count': len(anomaly_points),
                        'points': anomaly_points,
                        'percentage': (len(anomaly_points) / len(values)) * 100,
                        'note': 'Simple statistical detection (install scikit-learn for advanced detection)'
                    }
        
        return {
            'success': True,
            'anomalies': anomalies,
            'is_fallback': True,
            'timestamp': datetime.now().isoformat()
        }


# Instancia global
predictive_analyzer = PredictiveAnalyzer()


def predict_future(simulation_data: Dict, steps: int = 10) -> Dict:
    """Función wrapper para predicciones"""
    return predictive_analyzer.predict_future_values(simulation_data, steps)


def detect_anomalies(simulation_data: Dict) -> Dict:
    """Función wrapper para detección de anomalías"""
    return predictive_analyzer.detect_anomalies(simulation_data)


def analyze_correlations(simulation_data: Dict) -> Dict:
    """Función wrapper para análisis de correlaciones"""
    return predictive_analyzer.analyze_correlations(simulation_data)


def generate_forecast_report(simulation_data: Dict, parameters: Dict) -> Dict:
    """Función wrapper para reporte completo"""
    return predictive_analyzer.generate_forecast_report(simulation_data, parameters)
