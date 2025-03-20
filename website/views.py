from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Countdown, ToDo
from . import db
import json
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')  # Hidden input to differentiate forms

        if form_type == 'note':  # Handle Note submission
            note = request.form.get('note')
            if not note or len(note) < 1:
                flash('Note is too short!', category='error')
            else:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note Added!', category='success')

        elif form_type == 'countdown':  # Handle Countdown submission
            countdown_name = request.form.get('countdown_name')
            countdown_deadline = request.form.get('countdown_deadline')

            if countdown_name and countdown_deadline:
                try:
                    countdown_deadline = datetime.strptime(countdown_deadline, '%Y-%m-%d %H:%M')
                    new_countdown = Countdown(name=countdown_name, deadline=countdown_deadline, user_id=current_user.id)
                    db.session.add(new_countdown)
                    db.session.commit()
                    flash('Countdown Added!', category='success')
                except ValueError:
                    flash('Invalid date format. Use YYYY-MM-DD HH:MM.', category='error')

        elif form_type == 'todo':  # Handle To-Do submission
            task = request.form.get('task')
            if task:
                new_todo = ToDo(task=task, user_id=current_user.id)
                db.session.add(new_todo)
                db.session.commit()
                flash('To-Do Added!', category='success')

    # Get the user's notes, countdowns, and to-dos
    notes = Note.query.filter_by(user_id=current_user.id).all()
    countdowns = Countdown.query.filter_by(user_id=current_user.id).all()
    todos = ToDo.query.filter_by(user_id=current_user.id).all()  # Ensure you're passing the todos to the template

    return render_template('home.html', user=current_user, notes=notes, countdowns=countdowns, todos=todos)

@views.route('/add-note', methods=['POST'])
@login_required
def add_note():
    note_data = request.form.get('note')
    
    if not note_data or len(note_data) < 1:
        return jsonify({'success': False, 'message': 'Note is too short!'}), 400
    
    new_note = Note(data=note_data, user_id=current_user.id)
    db.session.add(new_note)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Note Added!', 'note': {'id': new_note.id, 'data': new_note.data}}), 200

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    try:
        note = json.loads(request.data)
        note_id = note.get('noteId')
        note_to_delete = Note.query.get(note_id)

        if note_to_delete and note_to_delete.user_id == current_user.id:
            db.session.delete(note_to_delete)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Note Deleted!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Note not found or unauthorized.'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)}), 500

@views.route('/delete-countdown', methods=['POST'])
@login_required
def delete_countdown():
    try:
        countdown = json.loads(request.data)
        countdown_id = countdown.get('countdownId')
        countdown_to_delete = Countdown.query.get(countdown_id)

        if countdown_to_delete and countdown_to_delete.user_id == current_user.id:
            db.session.delete(countdown_to_delete)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Countdown Deleted!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Countdown not found or unauthorized.'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)}), 500

@views.route('/add-todo', methods=['POST'])
@login_required
def add_todo():
    task = request.form.get('task')
    
    if not task or len(task) < 1:
        return jsonify({'success': False, 'message': 'Task cannot be empty!'}), 400
    
    new_todo = ToDo(task=task, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Task Added!', 'todo': {'id': new_todo.id, 'task': new_todo.task}}), 200

@views.route('/delete-todo', methods=['POST'])
@login_required
def delete_todo():
    try:
        data = json.loads(request.data)
        todo_id = data.get('todoId')
        todo_to_delete = ToDo.query.get(todo_id)

        if todo_to_delete and todo_to_delete.user_id == current_user.id:
            db.session.delete(todo_to_delete)
            db.session.commit()
            return jsonify({'success': True, 'message': 'To-Do Deleted!'}), 200
        else:
            return jsonify({'success': False, 'message': 'To-Do not found or unauthorized.'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)}), 500
    
@views.route('/toggle-todo-completion', methods=['POST'])
@login_required
def toggle_todo_completion():
    try:
        data = json.loads(request.data)
        todo_id = data.get('todoId')
        
        # Fetch the to-do item by ID
        todo = ToDo.query.get(todo_id)

        if todo and todo.user_id == current_user.id:
            # Toggle the completion status
            todo.completed = not todo.completed
            db.session.commit()
            return jsonify({'success': True, 'message': 'To-Do Completion Toggled!'}), 200
        else:
            return jsonify({'success': False, 'message': 'To-Do not found or unauthorized.'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)}), 500