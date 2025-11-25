from flask import render_template,make_response,request,jsonify
from src.Controllers.controller import controller
from src.Controllers.diagram_generator import generate_forrester_diagram, generate_causal_diagram
import os

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
        