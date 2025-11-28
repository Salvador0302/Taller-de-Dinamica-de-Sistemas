from flask import render_template,make_response,request,jsonify,send_file
from src.Controllers.controller import controller
from src.Controllers.diagram_generator import generate_forrester_diagram, generate_causal_diagram
from src.Controllers.export_controller import export_to_excel, export_to_csv, generate_pdf_report
from src.Controllers.scenario_controller import (
    create_scenario, compare_scenarios, get_scenario, 
    list_scenarios, delete_scenario, export_scenario, import_scenario
)
from src.Controllers.ai_assistant_controller import (
    analyze_simulation, ask_ai, get_parameter_suggestions,
    get_chat_history, clear_chat_history
)
from src.Controllers.predictive_controller import (
    predict_future, detect_anomalies, analyze_correlations, generate_forecast_report
)
import os
from datetime import datetime
from io import BytesIO

def modelRoute(app):
    @app.route('/', methods=['GET'])
    def model():
        response = controller()
        #print(response)
        if not (isinstance(response, dict) and len(response) == 0):
            if not (isinstance(response, list) and 'message' in response[0]):
                respuesta = make_response(render_template('template.html', nivel=response))
                respuesta.headers['Cache-Control'] = 'public, max-age=180'
                respuesta.headers['X-Content-Type-Options'] = 'nosniff'
                respuesta.headers['Server'] = 'Nombre del servidor'
                return respuesta
            else:
                respuesta = make_response(render_template('error.html', error_message=response))
                return respuesta
        else:
            respuesta = make_response(render_template('error.html', error_message=response))
            return respuesta
    
    @app.route('/api/update-simulation', methods=['POST'])
    def update_simulation():
        try:
            params = request.json
            print(f"API: Parámetros recibidos: {params}")
            response = controller(params=params)
            print(f"API: Tipo de respuesta: {type(response)}")
            print(f"API: Número de elementos: {len(response) if isinstance(response, (dict, list)) else 'N/A'}")
            
            if not (isinstance(response, list) and 'message' in response[0]):
                return jsonify({'success': True, 'data': response})
            else:
                return jsonify({'success': False, 'error': response[0]['message']})
        except Exception as e:
            print(f"API ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/diagrama-causal', methods=['GET'])
    def diagrama_causal():
        try:
            model_path = os.path.join('static', 'vensim', 'taller5_forrester.mdl')
            diagram_image = generate_causal_diagram(model_path)
            
            respuesta = make_response(render_template('diagrama_causal.html', diagram=diagram_image))
            respuesta.headers['Cache-Control'] = 'public, max-age=180'
            return respuesta
        except Exception as e:
            print(f"Error generando diagrama causal: {str(e)}")
            respuesta = make_response(render_template('diagrama_causal.html', diagram=None, error=str(e)))
            return respuesta
    
    @app.route('/diagrama-forrester', methods=['GET'])
    def diagrama_forrester():
        try:
            model_path = os.path.join('static', 'vensim', 'taller5_forrester.mdl')
            diagram_image = generate_forrester_diagram(model_path)
            
            respuesta = make_response(render_template('diagrama_forrester.html', diagram=diagram_image))
            respuesta.headers['Cache-Control'] = 'public, max-age=180'
            return respuesta
        except Exception as e:
            print(f"Error generando diagrama de Forrester: {str(e)}")
            respuesta = make_response(render_template('diagrama_forrester.html', diagram=None, error=str(e)))
            return respuesta

    # NOTE: Diagram images are now served from static/images/ (no custom route needed)
    
    @app.route('/api/export/excel', methods=['POST'])
    def export_excel():
        try:
            data = request.json
            simulation_data = data.get('data', {})
            
            excel_file = export_to_excel(simulation_data)
            filename = f"simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            return send_file(
                excel_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/export/csv', methods=['POST'])
    def export_csv():
        try:
            data = request.json
            simulation_data = data.get('data', {})
            
            csv_content = export_to_csv(simulation_data)
            filename = f"simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return send_file(
                BytesIO(csv_content.encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/export/pdf', methods=['POST'])
    def export_pdf():
        try:
            data = request.json
            simulation_data = data.get('data', {})
            parameters = data.get('parameters', None)
            
            pdf_file = generate_pdf_report(simulation_data, parameters)
            if pdf_file is None:
                return jsonify({'success': False, 'error': 'ReportLab no está instalado'}), 500
            
            filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return send_file(
                pdf_file,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ================== RUTAS DE ESCENARIOS ==================
    
    @app.route('/api/scenarios/create', methods=['POST'])
    def create_scenario_route():
        try:
            data = request.json
            name = data.get('name', 'Escenario sin nombre')
            description = data.get('description', '')
            parameters = data.get('parameters', {})
            
            result = create_scenario(name, description, parameters)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/list', methods=['GET'])
    def list_scenarios_route():
        try:
            scenarios = list_scenarios()
            return jsonify({'success': True, 'scenarios': scenarios})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/get/<scenario_id>', methods=['GET'])
    def get_scenario_route(scenario_id):
        try:
            scenario = get_scenario(scenario_id)
            if scenario:
                return jsonify({'success': True, 'scenario': scenario})
            else:
                return jsonify({'success': False, 'error': 'Scenario not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/compare', methods=['POST'])
    def compare_scenarios_route():
        try:
            data = request.json
            scenario_ids = data.get('scenario_ids', [])
            
            result = compare_scenarios(scenario_ids)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/delete/<scenario_id>', methods=['DELETE'])
    def delete_scenario_route(scenario_id):
        try:
            success = delete_scenario(scenario_id)
            if success:
                return jsonify({'success': True, 'message': 'Scenario deleted'})
            else:
                return jsonify({'success': False, 'error': 'Scenario not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/export/<scenario_id>', methods=['GET'])
    def export_scenario_route(scenario_id):
        try:
            scenario_json = export_scenario(scenario_id)
            if scenario_json:
                return send_file(
                    BytesIO(scenario_json.encode()),
                    mimetype='application/json',
                    as_attachment=True,
                    download_name=f'scenario_{scenario_id}.json'
                )
            else:
                return jsonify({'success': False, 'error': 'Scenario not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/import', methods=['POST'])
    def import_scenario_route():
        try:
            data = request.json
            scenario_json = data.get('scenario_json', '')
            
            result = import_scenario(scenario_json)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ================== RUTAS DEL ASISTENTE AI ==================
    
    @app.route('/api/ai/analyze', methods=['POST'])
    def ai_analyze_route():
        try:
            data = request.json
            simulation_data = data.get('simulation_data', {})
            parameters = data.get('parameters', {})
            
            result = analyze_simulation(simulation_data, parameters)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/ask', methods=['POST'])
    def ai_ask_route():
        try:
            data = request.json
            question = data.get('question', '')
            context = data.get('context', None)
            
            result = ask_ai(question, context)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/suggest-parameters', methods=['POST'])
    def ai_suggest_parameters_route():
        try:
            data = request.json
            current_params = data.get('current_params', {})
            goal = data.get('goal', '')
            simulation_data = data.get('simulation_data', None)
            
            result = get_parameter_suggestions(current_params, goal, simulation_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/history', methods=['GET'])
    def ai_history_route():
        try:
            history = get_chat_history()
            return jsonify({'success': True, 'history': history})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/clear-history', methods=['POST'])
    def ai_clear_history_route():
        try:
            clear_chat_history()
            return jsonify({'success': True, 'message': 'History cleared'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ================== RUTAS DE ANÁLISIS PREDICTIVO ==================
    
    @app.route('/api/predictive/forecast', methods=['POST'])
    def predictive_forecast_route():
        try:
            data = request.json
            simulation_data = data.get('simulation_data', {})
            steps = data.get('steps', 10)
            
            result = predict_future(simulation_data, steps)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/predictive/anomalies', methods=['POST'])
    def predictive_anomalies_route():
        try:
            data = request.json
            simulation_data = data.get('simulation_data', {})
            
            result = detect_anomalies(simulation_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/predictive/correlations', methods=['POST'])
    def predictive_correlations_route():
        try:
            data = request.json
            simulation_data = data.get('simulation_data', {})
            
            result = analyze_correlations(simulation_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/predictive/report', methods=['POST'])
    def predictive_report_route():
        try:
            data = request.json
            simulation_data = data.get('simulation_data', {})
            parameters = data.get('parameters', {})
            
            result = generate_forecast_report(simulation_data, parameters)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500