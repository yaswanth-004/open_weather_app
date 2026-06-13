import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database.db import db, WeatherSearch
from app.util.helper import (
    login_required, rate_limit_required,
    get_rate_limit_info, increment_rate_limit
)
from app.weather.service import (
    get_coordinates, get_today_weather,
    get_forecast, analyze_weather
)

weather_bp = Blueprint('weather', __name__, url_prefix='/weather')


@weather_bp.route('/', methods=['GET', 'POST'])
@login_required
@rate_limit_required
def index():
    """Main weather search page."""
    rate_info = get_rate_limit_info(session['user_id'])
    return render_template('weather.html', rate_info=rate_info)


@weather_bp.route('/today', methods=['POST'])
@login_required
@rate_limit_required
def today():
    """Fetch today's weather, analyze it, save to DB, show on home."""
    country  = request.form.get('country', '').strip()
    city     = request.form.get('city', '').strip()
    zip_code = request.form.get('zip_code', '').strip()

    if not country or not city:
        flash('Country and city are required.', 'danger')
        return redirect(url_for('weather.index'))

    try:
        lat, lon, display_name = get_coordinates(country, city, zip_code)
        weather = get_today_weather(lat, lon)
        weather = analyze_weather(weather)

        # Count this as one API call
        increment_rate_limit(session['user_id'])

        # Save search to DB
        record = WeatherSearch(
            city=city, country=country, zip_code=zip_code,
            latitude=lat, longitude=lon,
            weather_json=json.dumps(weather),
            search_type='today',
            user_id=session['user_id']
        )
        db.session.add(record)
        db.session.commit()

        rate_info = get_rate_limit_info(session['user_id'])
        return render_template('home.html',
                               weather=weather,
                               search_type='today',
                               rate_info=rate_info,
                               username=session.get('username'))

    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('weather.index'))
    except Exception as e:
        flash(f'API error: {str(e)}', 'danger')
        return redirect(url_for('weather.index'))


@weather_bp.route('/forecast', methods=['POST'])
@login_required
@rate_limit_required
def forecast():
    """Fetch 5-day forecast, save to DB, show on forecast page."""
    country  = request.form.get('country', '').strip()
    city     = request.form.get('city', '').strip()
    zip_code = request.form.get('zip_code', '').strip()

    if not country or not city:
        flash('Country and city are required.', 'danger')
        return redirect(url_for('weather.index'))

    try:
        lat, lon, display_name = get_coordinates(country, city, zip_code)
        forecast_days, raw_json = get_forecast(lat, lon)

        increment_rate_limit(session['user_id'])

        record = WeatherSearch(
            city=city, country=country, zip_code=zip_code,
            latitude=lat, longitude=lon,
            forecast_json=raw_json,
            search_type='forecast',
            user_id=session['user_id']
        )
        db.session.add(record)
        db.session.commit()

        rate_info = get_rate_limit_info(session['user_id'])
        return render_template('forecast.html',
                               forecast=forecast_days,
                               city=city, country=country,
                               rate_info=rate_info,
                               username=session.get('username'))

    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('weather.index'))
    except Exception as e:
        flash(f'API error: {str(e)}', 'danger')
        return redirect(url_for('weather.index'))


@weather_bp.route('/rate-limit')
def rate_limit_page():
    """Shown when user exceeds daily API limit."""
    rate_info = get_rate_limit_info(session.get('user_id', 0))
    return render_template('rate_limit.html', rate_info=rate_info), 429