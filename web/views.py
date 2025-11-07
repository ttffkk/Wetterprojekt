import yaml
from flask import Blueprint, render_template, request, jsonify, Response
from backend.analysis import Analysis
from data_ingestion.database import Database
import matplotlib.pyplot as plt
import io
import base64
import csv
from datetime import datetime, timedelta

web_blueprint = Blueprint('web', __name__)

@web_blueprint.route('/parameters')
def get_parameters():
    """Get all available parameters from the database."""
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    db_config = config['database']
    file_properties_config = config['source']['file_properties']

    db = Database(db_config['path'], file_properties_config['na_value'], file_properties_config['file_encoding'])
    db.create_connection()
    parameters = db.get_all_parameters()
    db.close_connection()

    return jsonify(parameters)

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

    # Get interpolated weather data
    weather_data = analysis.interpolate_weather_data(location, date)

    db.close_connection()

    if weather_data is None:
        return jsonify({'error': 'Could not retrieve weather data.'}), 400

    return jsonify(weather_data)

@web_blueprint.route('/plot_data', methods=['POST'])
def plot_data():
    """
    Generate a plot for a specific location, date range and parameter.
    ---
    parameters:
      - name: location
        in: formData
        type: string
        required: true
        description: The address in Germany to get weather data for.
      - name: start_date
        in: formData
        type: string
        format: date
        required: true
        description: The start date for the plot.
      - name: end_date
        in: formData
        type: string
        format: date
        required: true
        description: The end date for the plot.
      - name: parameter
        in: formData
        type: string
        required: true
        description: The parameter to plot.
    responses:
      200:
        description: A base64 encoded PNG image of the plot.
        schema:
          type: string
          format: byte
      400:
        description: Invalid input or no data available.
    """
    location = request.form.get('location')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    parameter = request.form.get('parameter')

    if not location or not start_date_str or not end_date_str or not parameter:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if start_date > end_date:
        return jsonify({'error': 'Start date cannot be after end date.'}), 400

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

    # Get all parameters from the database
    parameters = {p[0]: (p[1], p[2]) for p in db.get_all_parameters()}
    if parameter not in parameters:
        return jsonify({'error': 'Invalid parameter.'}), 400

    dates = []
    values = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        data = analysis.interpolate_weather_data(location, date_str)
        if data and data.get(parameter) is not None:
            dates.append(current_date)
            values.append(data[parameter])
        current_date += timedelta(days=1)

    db.close_connection()

    if not dates:
        return jsonify({'error': 'No weather data available for the specified period.'}), 400

    # Generate plot
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel(f'{parameters[parameter][0]} ({parameters[parameter][1]})')
    plt.title(f'{parameters[parameter][0]} for {location} ({start_date_str} to {end_date_str})')
    plt.grid(True)
    plt.tight_layout()

    # Save plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close() # Close the plot to free up memory

    # Encode image to base64
    plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return jsonify({'plot': plot_base64})

@web_blueprint.route('/export_csv', methods=['POST'])
def export_csv():
    """
    Export weather data to a CSV file.
    ---
    parameters:
      - name: location
        in: formData
        type: string
        required: true
        description: The address in Germany to get weather data for.
      - name: start_date
        in: formData
        type: string
        format: date
        required: true
        description: The start date for the CSV export.
      - name: end_date
        in: formData
        type: string
        format: date
        required: true
        description: The end date for the CSV export.
    responses:
      200:
        description: A CSV file with the weather data.
        content:
          text/csv:
            schema:
              type: string
      400:
        description: Invalid input or no data available.
    """
    location = request.form.get('location')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    if not location or not start_date_str or not end_date_str:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if start_date > end_date:
        return jsonify({'error': 'Start date cannot be after end date.'}), 400

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

    weather_data = analysis.get_weather_data_for_period(location, start_date_str, end_date_str)

    db.close_connection()

    if not weather_data or len(weather_data) <= 1:
        return jsonify({'error': 'No weather data available for the specified period.'}), 400

    # Create a string buffer for the CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(weather_data)

    # Create a response with the CSV data
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename=weather_data_{location}_{start_date_str}_{end_date_str}.csv"}
    )