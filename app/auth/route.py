from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database.db import db, User, bcrypt

from app.auth import bp

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, go to blog home
    if 'user_id' in session:
        return redirect(url_for('blog.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        # Role: form sends 'admin' only if user picks it AND enters admin code
        role     = request.form.get('role', 'user')
        admin_code = request.form.get('admin_code', '')

        # Basic validation
        if not all([username, email, phone, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        # Admin code check (set your own secret in .env)
        ADMIN_SECRET = 'MYADMIN123'  # move this to config later
        if role == 'admin' and admin_code != ADMIN_SECRET:
            flash('Invalid admin code.', 'danger')
            return render_template('register.html')

        # Check duplicates
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        # Create user
        user = User(username=username, email=email, phone=phone, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('blog.home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Store everything you need in session
            session.permanent = True          # respects PERMANENT_SESSION_LIFETIME
            session['user_id']  = user.ID
            session['username'] = user.username
            session['role']     = user.role

            flash(f'Welcome back, {user.username}!', 'success')

            # Redirect to the page they tried to visit, or blog home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('blog.home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))