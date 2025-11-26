"""
Controlador para gestión de escenarios de simulación
Permite crear, guardar y comparar múltiples escenarios con diferentes parámetros
"""
import json
from datetime import datetime
from src.Controllers.controller import controller


class ScenarioManager:
    """Gestor de escenarios de simulación"""
    
    def __init__(self):
        self.scenarios = {}
    
    def create_scenario(self, name, description, parameters):
        """
        Crea un nuevo escenario con parámetros específicos
        
        Args:
            name (str): Nombre del escenario
            description (str): Descripción del escenario
            parameters (dict): Parámetros de simulación
        
        Returns:
            dict: Escenario creado con resultados de simulación
        """
        scenario_id = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Ejecutar simulación con los parámetros dados
        simulation_results = controller(params=parameters)
        
        if isinstance(simulation_results, list) and 'message' in simulation_results[0]:
            return {
                'success': False,
                'error': simulation_results[0]['message']
            }
        
        scenario = {
            'id': scenario_id,
            'name': name,
            'description': description,
            'parameters': parameters,
            'results': simulation_results,
            'created_at': datetime.now().isoformat(),
            'metadata': self._extract_metadata(simulation_results)
        }
        
        self.scenarios[scenario_id] = scenario
        
        return {
            'success': True,
            'scenario': scenario
        }
    
    def _extract_metadata(self, simulation_results):
        """
        Extrae metadata resumida de los resultados de simulación
        
        Args:
            simulation_results (dict): Resultados de la simulación
        
        Returns:
            dict: Metadata con estadísticas por variable
        """
        metadata = {}
        
        for var_name, var_data in simulation_results.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                values = list(var_data['data'].values())
                if values:
                    metadata[var_name] = {
                        'initial': values[0],
                        'final': values[-1],
                        'max': max(values),
                        'min': min(values),
                        'avg': sum(values) / len(values),
                        'change_percent': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                    }
        
        return metadata
    
    def compare_scenarios(self, scenario_ids):
        """
        Compara múltiples escenarios
        
        Args:
            scenario_ids (list): Lista de IDs de escenarios a comparar
        
        Returns:
            dict: Datos comparativos de los escenarios
        """
        if not scenario_ids:
            return {
                'success': False,
                'error': 'No scenarios provided for comparison'
            }
        
        comparison_data = {
            'scenarios': [],
            'variables': set(),
            'comparative_data': {}
        }
        
        # Recopilar datos de cada escenario
        for scenario_id in scenario_ids:
            if scenario_id in self.scenarios:
                scenario = self.scenarios[scenario_id]
                comparison_data['scenarios'].append({
                    'id': scenario['id'],
                    'name': scenario['name'],
                    'parameters': scenario['parameters'],
                    'metadata': scenario['metadata']
                })
                
                # Recopilar nombres de variables
                for var_name in scenario['results'].keys():
                    comparison_data['variables'].add(var_name)
        
        comparison_data['variables'] = list(comparison_data['variables'])
        
        # Preparar datos comparativos por variable
        for var_name in comparison_data['variables']:
            comparison_data['comparative_data'][var_name] = []
            
            for scenario_id in scenario_ids:
                if scenario_id in self.scenarios:
                    scenario = self.scenarios[scenario_id]
                    if var_name in scenario['results']:
                        var_data = scenario['results'][var_name]
                        if isinstance(var_data, dict) and 'data' in var_data:
                            comparison_data['comparative_data'][var_name].append({
                                'scenario_id': scenario_id,
                                'scenario_name': scenario['name'],
                                'data': var_data['data'],
                                'title': var_data.get('title', var_name),
                                'xlabel': var_data.get('xlabel', 'Tiempo'),
                                'ylabel': var_data.get('ylabel', 'Valor')
                            })
        
        return {
            'success': True,
            'comparison': comparison_data
        }
    
    def get_scenario(self, scenario_id):
        """
        Obtiene un escenario específico
        
        Args:
            scenario_id (str): ID del escenario
        
        Returns:
            dict: Datos del escenario o None si no existe
        """
        return self.scenarios.get(scenario_id)
    
    def list_scenarios(self):
        """
        Lista todos los escenarios creados
        
        Returns:
            list: Lista de escenarios (sin resultados completos para reducir tamaño)
        """
        scenarios_list = []
        
        for scenario_id, scenario in self.scenarios.items():
            scenarios_list.append({
                'id': scenario['id'],
                'name': scenario['name'],
                'description': scenario['description'],
                'parameters': scenario['parameters'],
                'metadata': scenario['metadata'],
                'created_at': scenario['created_at']
            })
        
        return scenarios_list
    
    def delete_scenario(self, scenario_id):
        """
        Elimina un escenario
        
        Args:
            scenario_id (str): ID del escenario a eliminar
        
        Returns:
            bool: True si se eliminó, False si no existía
        """
        if scenario_id in self.scenarios:
            del self.scenarios[scenario_id]
            return True
        return False
    
    def export_scenario(self, scenario_id):
        """
        Exporta un escenario a formato JSON
        
        Args:
            scenario_id (str): ID del escenario
        
        Returns:
            str: JSON del escenario
        """
        scenario = self.scenarios.get(scenario_id)
        if scenario:
            return json.dumps(scenario, indent=2)
        return None
    
    def import_scenario(self, scenario_json):
        """
        Importa un escenario desde JSON
        
        Args:
            scenario_json (str): JSON del escenario
        
        Returns:
            dict: Resultado de la importación
        """
        try:
            scenario = json.loads(scenario_json)
            scenario_id = scenario.get('id', f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            self.scenarios[scenario_id] = scenario
            return {
                'success': True,
                'scenario_id': scenario_id
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': str(e)
            }


# Instancia global del gestor de escenarios
scenario_manager = ScenarioManager()


def create_scenario(name, description, parameters):
    """Función wrapper para crear escenario"""
    return scenario_manager.create_scenario(name, description, parameters)


def compare_scenarios(scenario_ids):
    """Función wrapper para comparar escenarios"""
    return scenario_manager.compare_scenarios(scenario_ids)


def get_scenario(scenario_id):
    """Función wrapper para obtener escenario"""
    return scenario_manager.get_scenario(scenario_id)


def list_scenarios():
    """Función wrapper para listar escenarios"""
    return scenario_manager.list_scenarios()


def delete_scenario(scenario_id):
    """Función wrapper para eliminar escenario"""
    return scenario_manager.delete_scenario(scenario_id)


def export_scenario(scenario_id):
    """Función wrapper para exportar escenario"""
    return scenario_manager.export_scenario(scenario_id)


def import_scenario(scenario_json):
    """Función wrapper para importar escenario"""
    return scenario_manager.import_scenario(scenario_json)
