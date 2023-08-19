from flask import render_template, request, redirect, session, flash
from flask_app import app
from flask_app.models import show


#GET routes
@app.route('/show/like/<int:show_id>')
def show_like(show_id):
    show.Show.like_show(show_id,session['user_id'])
    return redirect('/show/list')

@app.route('/show/unlike/<int:show_id>')
def show_unlike(show_id):
    show.Show.unlike_show(show_id,session['user_id'])
    return redirect('/show/list')

@app.route('/show/list')
def show_list_page():
    if 'user_id' not in session: #probably should make this a function because I keep repeating it
        session.clear()
        flash('You have been logged out.',"registration")
        return redirect('/')
    shows_list = show.Show.get_all()
    return render_template('show_list.html', shows=shows_list)

@app.route('/show/add')
def add_show_page():
    if 'user_id' not in session:
        session.clear()
        flash('You have been logged out.',"registration")
        return redirect('/')
    return render_template('show_add.html')

@app.route('/show/detail/<int:show_id>')
def show_detail_page(show_id):
    if 'user_id' not in session:
        session.clear()
        flash('You have been logged out.',"registration")
        return redirect('/')
    show_obj = show.Show.get_one_by_id(show_id)
    return render_template('show_detail.html',show=show_obj)

@app.route('/show/delete/<int:show_id>')
def show_delete(show_id):
    show_obj = show.Show.get_one_by_id(show_id)
    if not session['user_id'] == show_obj.owner.id:
        session.clear()
        flash('You have been logged out.',"registration")
        return redirect('/')
    else:
        show.Show.delete(show_id)
        return redirect('/show/list')

@app.route('/show/edit/<int:show_id>')
def show_edit_page(show_id):
    show_obj = show.Show.get_one_by_id(show_id)
    if not session['user_id'] == show_obj.owner.id:
        session.clear()
        flash('You have been logged out.',"registration")
        return redirect('/')
    session['show_id'] = show_obj.id
    session['title'] = show_obj.title
    session['network'] = show_obj.network
    session['description'] = show_obj.description
    session['user_id'] = show_obj.owner.id
    session['release_date'] = show_obj.release_date
    return render_template('show_edit.html')

#POST routes
@app.route('/show/create', methods=['post'])
def create_show():
    if show.Show.show_is_valid(request.form):
        show.Show.save(request.form)
        # clear session variables for ride if it does save    
        session.pop('title', None)
        session.pop('network', None)
        session.pop('release_date', None)
        session.pop('description', None)
        return redirect('/show/list') # redirect to show list
    else: #failed validations
        # Create session variables for ride if it doesn't save
        session['title'] = request.form['title']
        session['network'] = request.form['network']
        session['release_date'] = request.form['release_date']
        session['description'] = request.form['description']
        return redirect('/show/add') #redirect to same page
    
@app.route('/show/update', methods=['post'])
def update_show():
    if show.Show.show_is_valid(request.form):
        show.Show.update(request.form)
        # clear session variables for show if it does save    
        session.pop('title', None)
        session.pop('network', None)
        session.pop('description', None)
        session.pop('release_date', None)
        return redirect('/show/list') # redirect to show list
    else: #failed validations
        # Create session variables for show if it doesn't save
        session['title'] = request.form['title']
        session['network'] = request.form['network']
        session['description'] = request.form['description']
        session['release_date'] = request.form['release_date']
        return redirect(f"/show/edit/{request.form['id']}") #redirect to same page