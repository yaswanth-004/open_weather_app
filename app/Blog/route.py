from flask import Blueprint, render_template, session
from app.database.db import Post
from app.util.helper import login_required, admin_required
from app.Blog import pb


@pb.route('/home')
@login_required          # ← blocks access if not logged in
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', posts=posts,
                           username=session.get('username'),
                           role=session.get('role'))


# Example admin-only route (for later)
@pb.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')