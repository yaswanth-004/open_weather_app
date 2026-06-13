from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.database.db import db, User, WeatherSearch
from app.util.helper import login_required, get_rate_limit_info

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@login_required
def view():
    user = User.query.get(session['user_id'])
    searches = WeatherSearch.query.filter_by(
        user_id=session['user_id']
    ).order_by(WeatherSearch.searched_at.desc()).limit(20).all()
    rate_info = get_rate_limit_info(session['user_id'])
    return render_template('profile.html',
                           user=user,
                           searches=searches,
                           rate_info=rate_info)


@profile_bp.route('/update', methods=['POST'])
@login_required
def update():
    user = User.query.get(session['user_id'])
    username     = request.form.get('username', '').strip()
    email        = request.form.get('email', '').strip()
    phone        = request.form.get('phone', '').strip()
    new_password = request.form.get('new_password', '')
    confirm      = request.form.get('confirm_password', '')

    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            flash('Username taken.', 'danger')
            return redirect(url_for('profile.view'))
        user.username = username
        session['username'] = username

    if email:
        user.email = email
    if phone:
        user.phone = phone

    if new_password:
        if new_password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('profile.view'))
        user.set_password(new_password)

    db.session.commit()
    flash('Profile updated.', 'success')
    return redirect(url_for('profile.view'))


@profile_bp.route('/delete', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash('Account deleted.', 'info')
    return redirect(url_for('auth.register'))