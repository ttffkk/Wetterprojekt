import yaml
from flask import Blueprint, render_template, request, jsonify
from backend.analysis import Analysis
from data_ingestion.database import Database

web_blueprint = Blueprint('web', __name__)

@web_blueprint.route('/')
def index():
    """Homepage of the DWD Weather Analysis application.
    ---
    responses:
      200:
        description: The homepage of the application.
    """
    return render_template('index.html')

@web_blueprint.route('/weather', methods=['POST'])
def get_weather():
    """
    Get weather data for a specific location and date.
    ---
    parameters:
      - name: location
        in: formData
        type: string
        required: true
        description: The address in Germany to get weather data for.
      - name: date
        in: formData
        type: string
        format: date
        required: true
        description: The date to get weather data for.
    responses:
      200:
        description: The interpolated weather data.
        schema:
          type: object
          properties:
            temperature:
              type: number
              description: The interpolated temperature in Celsius.
      400:
        description: Invalid input.
    """
    location = request.form.get('location')
    date = request.form.get('date')

    if not location or not date:
        return jsonify({'error': 'Invalid input'}), 400

    # Load configuration from YAML file
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    db_config = config['database']
    source_config = config['source']
    file_properties_config = source_config['file_properties']

    # Initialize database and analysis
    db = Database(db_config['path'], file_properties_config['na_value'], file_properties_config['file_encoding'])
    db.create_connection()
    analysis = Analysis(db)

    # Get interpolated temperature
    temperature = analysis.interpolate_weather_data(location, date)

    db.close_connection()

    if temperature is None:
        return jsonify({'error': 'Could not retrieve weather data.'}), 400

    return jsonify({'temperature': temperature})