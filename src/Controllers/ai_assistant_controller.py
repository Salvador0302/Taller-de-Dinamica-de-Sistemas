"""
Controlador del Asistente AI
Integra OpenAI/Claude para análisis inteligente de simulaciones
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional


class AIAssistant:
    """Asistente AI para análisis de simulaciones"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        """
        Inicializa el asistente AI
        
        Args:
            api_key: Clave API (OpenAI, Anthropic o Google Gemini)
            provider: 'openai', 'anthropic' o 'gemini'
        """
        self.provider = provider
        # Priorizar Gemini con la API key proporcionada
        if provider == "gemini":
            self.api_key = "AIzaSyCwY35lVkIW72DjUi2O7MO9Xeze1rge3Qs"
        else:
            self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.conversation_history = []
        self.client = None
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa el cliente de la API"""
        try:
            if self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # Usar gemini-2.5-flash (modelo disponible en 2025)
                try:
                    self.client = genai.GenerativeModel('gemini-2.5-flash')
                    # Probar con una consulta simple
                    test = self.client.generate_content("test")
                    print("✅ Gemini AI 2.5 Flash inicializado correctamente")
                except Exception as e:
                    print(f"⚠️  Gemini API key no válida o expirada: {e}")
                    print("📊 Usando modo de análisis estadístico básico")
                    self.client = None
            elif self.provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            elif self.provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError as e:
            print(f"Warning: {self.provider} library not installed: {e}")
            self.client = None
        except Exception as e:
            print(f"Error initializing {self.provider}: {e}")
            self.client = None
    
    def analyze_simulation_results(self, simulation_data: Dict, parameters: Dict) -> Dict:
        """
        Analiza resultados de simulación y genera insights
        
        Args:
            simulation_data: Datos de la simulación
            parameters: Parámetros utilizados
        
        Returns:
            Dict con análisis, insights y recomendaciones
        """
        if not self.client:
            return self._generate_fallback_analysis(simulation_data, parameters)
        
        # Preparar contexto para el AI
        context = self._prepare_simulation_context(simulation_data, parameters)
        
        prompt = f"""Eres un experto en dinámica de sistemas analizando una simulación sobre inmigración, delincuencia y seguridad pública.

DATOS DE LA SIMULACIÓN:
{json.dumps(context, indent=2, ensure_ascii=False)}

Por favor, proporciona un análisis detallado que incluya:

1. **Resumen Ejecutivo**: Síntesis de los resultados principales en 2-3 oraciones
2. **Tendencias Identificadas**: Patrones y comportamientos observados en cada variable
3. **Relaciones Causales**: Cómo los parámetros afectan los resultados
4. **Puntos Críticos**: Momentos o valores donde se observan cambios significativos
5. **Recomendaciones**: Sugerencias para optimizar el sistema (reducir delincuencia, optimizar recursos policiales, etc.)

Responde en español, de forma clara y profesional."""

        try:
            response = self._call_ai_api(prompt)
            
            return {
                'success': True,
                'analysis': response,
                'timestamp': datetime.now().isoformat(),
                'context': context
            }
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return self._generate_fallback_analysis(simulation_data, parameters)
    
    def ask_question(self, question: str, simulation_context: Optional[Dict] = None) -> Dict:
        """
        Responde preguntas del usuario sobre la simulación
        
        Args:
            question: Pregunta del usuario
            simulation_context: Contexto opcional de la simulación actual
        
        Returns:
            Dict con respuesta del AI
        """
        if not self.client:
            return {
                'success': False,
                'error': 'AI Assistant no disponible. Configura tu API key.',
                'answer': 'Lo siento, necesito una clave API para responder preguntas.'
            }
        
        # Construir contexto
        context_str = ""
        if simulation_context:
            context_str = f"\n\nCONTEXTO DE LA SIMULACIÓN ACTUAL:\n{json.dumps(simulation_context, indent=2, ensure_ascii=False)}"
        
        prompt = f"""Eres un asistente experto en dinámica de sistemas especializado en modelos de inmigración, delincuencia y seguridad pública.
{context_str}

PREGUNTA DEL USUARIO:
{question}

Proporciona una respuesta clara, precisa y útil en español. Si la pregunta se relaciona con la simulación actual, usa los datos del contexto."""

        try:
            response = self._call_ai_api(prompt)
            
            # Agregar a historial
            self.conversation_history.append({
                'role': 'user',
                'content': question,
                'timestamp': datetime.now().isoformat()
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'question': question,
                'answer': response,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return {
                'success': False,
                'error': str(e),
                'answer': 'Lo siento, ocurrió un error al procesar tu pregunta.'
            }
    
    def suggest_parameters(self, current_params: Dict, goal: str, simulation_data: Optional[Dict] = None) -> Dict:
        """
        Sugiere ajustes de parámetros basados en un objetivo
        
        Args:
            current_params: Parámetros actuales
            goal: Objetivo deseado (ej: "reducir delincuencia", "optimizar policías")
            simulation_data: Datos de simulación actuales (opcional)
        
        Returns:
            Dict con sugerencias de parámetros
        """
        if not self.client:
            return self._generate_fallback_suggestions(current_params, goal)
        
        context = ""
        if simulation_data:
            stats = self._calculate_statistics(simulation_data)
            context = f"\n\nRESULTADOS ACTUALES:\n{json.dumps(stats, indent=2, ensure_ascii=False)}"
        
        prompt = f"""Eres un experto en optimización de sistemas dinámicos de inmigración y seguridad pública.

PARÁMETROS ACTUALES:
{json.dumps(current_params, indent=2, ensure_ascii=False)}
{context}

OBJETIVO DEL USUARIO:
{goal}

Por favor, sugiere ajustes específicos a los parámetros para lograr este objetivo. Para cada parámetro que recomiendes cambiar:
1. Indica el valor actual
2. Sugiere el nuevo valor
3. Explica el razonamiento
4. Describe el impacto esperado

Responde en formato JSON con esta estructura:
{{
    "recommendations": [
        {{
            "parameter": "nombre_parametro",
            "current_value": valor_actual,
            "suggested_value": valor_sugerido,
            "reasoning": "explicación",
            "expected_impact": "impacto esperado"
        }}
    ],
    "overall_strategy": "estrategia general",
    "expected_outcome": "resultado esperado"
}}"""

        try:
            response = self._call_ai_api(prompt)
            
            # Intentar parsear JSON
            try:
                suggestions = json.loads(response)
            except json.JSONDecodeError:
                # Si no es JSON válido, envolver la respuesta
                suggestions = {
                    'recommendations': [],
                    'overall_strategy': response,
                    'expected_outcome': 'Ver análisis detallado'
                }
            
            return {
                'success': True,
                'suggestions': suggestions,
                'goal': goal,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return self._generate_fallback_suggestions(current_params, goal)
    
    def _call_ai_api(self, prompt: str) -> str:
        """Llama a la API del proveedor AI"""
        if self.provider == "gemini":
            try:
                response = self.client.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Gemini API error: {e}")
                # Fallback a análisis básico
                return "Lo siento, ocurrió un error al procesar con Gemini AI."
        
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # o "gpt-4" para mejor calidad
                messages=[
                    {"role": "system", "content": "Eres un experto en dinámica de sistemas y análisis de simulaciones."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        
        return ""
    
    def _prepare_simulation_context(self, simulation_data: Dict, parameters: Dict) -> Dict:
        """Prepara contexto estructurado de la simulación"""
        context = {
            'parameters': parameters,
            'statistics': self._calculate_statistics(simulation_data),
            'variables': list(simulation_data.keys())
        }
        return context
    
    def _calculate_statistics(self, simulation_data: Dict) -> Dict:
        """Calcula estadísticas de las variables"""
        stats = {}
        
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                values = list(var_data['data'].values())
                if values:
                    stats[var_name] = {
                        'initial': values[0],
                        'final': values[-1],
                        'max': max(values),
                        'min': min(values),
                        'average': sum(values) / len(values),
                        'change': values[-1] - values[0],
                        'change_percent': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                    }
        
        return stats
    
    def _generate_fallback_analysis(self, simulation_data: Dict, parameters: Dict) -> Dict:
        """Genera análisis básico sin AI"""
        stats = self._calculate_statistics(simulation_data)
        
        analysis_parts = ["## Análisis de la Simulación\n"]
        
        # Resumen
        analysis_parts.append("### 📊 Resumen Ejecutivo\n")
        analysis_parts.append(f"Simulación ejecutada con {len(stats)} variables monitoreadas.\n\n")
        
        # Estadísticas por variable
        analysis_parts.append("### 📈 Estadísticas por Variable\n")
        for var_name, var_stats in stats.items():
            change_emoji = "📈" if var_stats['change'] > 0 else "📉"
            analysis_parts.append(f"\n**{var_name}** {change_emoji}\n")
            analysis_parts.append(f"- Valor inicial: {var_stats['initial']:.2f}\n")
            analysis_parts.append(f"- Valor final: {var_stats['final']:.2f}\n")
            analysis_parts.append(f"- Cambio: {var_stats['change']:+.2f} ({var_stats['change_percent']:+.1f}%)\n")
            analysis_parts.append(f"- Rango: {var_stats['min']:.2f} - {var_stats['max']:.2f}\n")
        
        # Recomendaciones básicas
        analysis_parts.append("\n### 💡 Recomendaciones\n")
        analysis_parts.append("Configure una API key de OpenAI o Anthropic para obtener análisis avanzados con IA.\n")
        
        return {
            'success': True,
            'analysis': ''.join(analysis_parts),
            'timestamp': datetime.now().isoformat(),
            'context': {'parameters': parameters, 'statistics': stats},
            'is_fallback': True
        }
    
    def _generate_fallback_suggestions(self, current_params: Dict, goal: str) -> Dict:
        """Genera sugerencias básicas sin AI"""
        suggestions = {
            'recommendations': [],
            'overall_strategy': f"Para lograr '{goal}', considera ajustar los parámetros relacionados. Configure una API key para obtener sugerencias específicas con IA.",
            'expected_outcome': 'Análisis limitado sin IA'
        }
        
        return {
            'success': True,
            'suggestions': suggestions,
            'goal': goal,
            'timestamp': datetime.now().isoformat(),
            'is_fallback': True
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Obtiene el historial de conversación"""
        return self.conversation_history
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []


# Instancia global del asistente
ai_assistant = AIAssistant()


def analyze_simulation(simulation_data: Dict, parameters: Dict) -> Dict:
    """Función wrapper para análisis de simulación"""
    return ai_assistant.analyze_simulation_results(simulation_data, parameters)


def ask_ai(question: str, context: Optional[Dict] = None) -> Dict:
    """Función wrapper para preguntas al AI"""
    return ai_assistant.ask_question(question, context)


def get_parameter_suggestions(current_params: Dict, goal: str, simulation_data: Optional[Dict] = None) -> Dict:
    """Función wrapper para sugerencias de parámetros"""
    return ai_assistant.suggest_parameters(current_params, goal, simulation_data)


def get_chat_history() -> List[Dict]:
    """Función wrapper para obtener historial"""
    return ai_assistant.get_conversation_history()


def clear_chat_history():
    """Función wrapper para limpiar historial"""
    ai_assistant.clear_history()
