from functools import wraps
from datetime import datetime, date
from flask import session, url_for, redirect, flash, request, current_app
from app.database.db import db, RateLimit, User

# Minimum free attempts per user per day
MIN_FREE_ATTEMPTS = 20


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('blog.home'))
        return f(*args, **kwargs)
    return decorated


def get_rate_limit_info(user_id):
    """
    Returns dict with:
      - calls_today   : how many calls this user made today
      - limit         : their personal limit
      - remaining     : how many left
      - exceeded      : True/False
    
    Logic:
      total_users = count of all users
      capacity    = total_users * MIN_FREE_ATTEMPTS
      each user gets MIN_FREE_ATTEMPTS regardless
    """
    today = date.today()
    total_users = User.query.count() or 1

    # Capacity check — if total calls today across all users
    # exceeds total_users * MIN_FREE_ATTEMPTS, system is stressed
    total_calls_today = db.session.query(
        db.func.sum(RateLimit.call_count)
    ).filter(RateLimit.date == today).scalar() or 0

    capacity = total_users * MIN_FREE_ATTEMPTS

    # Get this user's record
    record = RateLimit.query.filter_by(
        user_id=user_id, date=today
    ).first()

    calls_today = record.call_count if record else 0
    remaining   = max(0, MIN_FREE_ATTEMPTS - calls_today)
    exceeded    = calls_today >= MIN_FREE_ATTEMPTS

    return {
        'calls_today':        calls_today,
        'limit':              MIN_FREE_ATTEMPTS,
        'remaining':          remaining,
        'exceeded':           exceeded,
        'total_users':        total_users,
        'total_calls_today':  total_calls_today,
        'capacity':           capacity,
        'system_stressed':    total_calls_today >= capacity,
    }


def increment_rate_limit(user_id):
    """Call this every time a real OpenWeather API hit is made."""
    today = date.today()
    record = RateLimit.query.filter_by(
        user_id=user_id, date=today
    ).first()
    if record:
        record.call_count += 1
    else:
        record = RateLimit(user_id=user_id, date=today, call_count=1)
        db.session.add(record)
    db.session.commit()


def rate_limit_required(f):
    """Decorator: blocks the route if user exceeded daily limit."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        info = get_rate_limit_info(session['user_id'])
        if info['exceeded']:
            return redirect(url_for('weather.rate_limit_page'))
        return f(*args, **kwargs)
    return decorated