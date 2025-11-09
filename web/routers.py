from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import yaml
from backend.analysis import Analysis
from data_ingestion.database import Database
import matplotlib.pyplot as plt
import io
import base64
import csv
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

# Dependency to get the database connection
def get_db():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    db_config = config['database']
    file_properties_config = config['source']['file_properties']
    db = Database(db_config['path'], file_properties_config['na_value'], file_properties_config['file_encoding'])
    db.create_connection()
    try:
        yield db
    finally:
        db.close_connection()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/parameters")
async def get_parameters(db: Database = Depends(get_db)):
    """Get all available parameters from the database."""
    parameters = db.get_all_parameters()
    return JSONResponse(content=parameters)

@router.post("/weather")
async def get_weather(location: str = Form(...), date: str = Form(...), db: Database = Depends(get_db)):
    """
    Get weather data for a specific location and date.
    """
    if not location or not date:
        return JSONResponse(content={'error': 'Invalid input'}, status_code=400)

    analysis = Analysis(db)
    weather_data = analysis.interpolate_weather_data(location, date)

    if weather_data is None:
        return JSONResponse(content={'error': 'Could not retrieve weather data.'}, status_code=400)

    return JSONResponse(content=weather_data)

@router.post("/plot_data")
async def plot_data(location: str = Form(...), start_date: str = Form(...), end_date: str = Form(...), parameter: str = Form(...), db: Database = Depends(get_db)):
    """
    Generate a plot for a specific location, date range and parameter.
    """
    if not location or not start_date or not end_date or not parameter:
        return JSONResponse(content={'error': 'Invalid input'}, status_code=400)

    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return JSONResponse(content={'error': 'Invalid date format. Use YYYY-MM-DD.'}, status_code=400)

    if start_date_obj > end_date_obj:
        return JSONResponse(content={'error': 'Start date cannot be after end date.'}, status_code=400)

    analysis = Analysis(db)
    parameters = {p[0]: (p[1], p[2]) for p in db.get_all_parameters()}
    if parameter not in parameters:
        return JSONResponse(content={'error': 'Invalid parameter.'}, status_code=400)

    dates = []
    values = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        date_str = current_date.strftime('%Y-%m-%d')
        data = analysis.interpolate_weather_data(location, date_str)
        if data and data.get(parameter) is not None:
            dates.append(current_date)
            values.append(data[parameter])
        current_date += timedelta(days=1)

    if not dates:
        return JSONResponse(content={'error': 'No weather data available for the specified period.'}, status_code=400)

    # Generate plot
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel(f'{parameters[parameter][0]} ({parameters[parameter][1]})')
    plt.title(f'{parameters[parameter][0]} for {location} ({start_date} to {end_date})')
    plt.grid(True)
    plt.tight_layout()

    # Save plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close() # Close the plot to free up memory

    # Encode image to base64
    plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return JSONResponse(content={'plot': plot_base64})

@router.post("/export_csv")
async def export_csv(location: str = Form(...), start_date: str = Form(...), end_date: str = Form(...), db: Database = Depends(get_db)):
    """
    Export weather data to a CSV file.
    """
    if not location or not start_date or not end_date:
        return JSONResponse(content={'error': 'Invalid input'}, status_code=400)

    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return JSONResponse(content={'error': 'Invalid date format. Use YYYY-MM-DD.'}, status_code=400)

    if start_date_obj > end_date_obj:
        return JSONResponse(content={'error': 'Start date cannot be after end date.'}, status_code=400)

    analysis = Analysis(db)
    weather_data = analysis.get_weather_data_for_period(location, start_date, end_date)

    if not weather_data or len(weather_data) <= 1:
        return JSONResponse(content={'error': 'No weather data available for the specified period.'}, status_code=400)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(weather_data)

    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition":
                 f"attachment; filename=weather_data_{location}_{start_date}_{end_date}.csv"}
    )
