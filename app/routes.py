from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Trip, Item

main_bp = Blueprint('main', __name__)

# 1. Главная страница: просмотр всех поездок + поиск
@main_bp.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    if search_query:
        # Реализация поиска/фильтрации по месту назначения
        trips = Trip.query.filter(Trip.location.ilike(f"%{search_query}%")).all()
    else:
        trips = Trip.query.all()
    return render_template('index.html', trips=trips, search_query=search_query)

# 2. Добавление новой поездки (Форма с POST)
@main_bp.route('/trip/add', methods=['POST'])
def add_trip():
    name = request.form.get('name', '').strip()
    dates = request.form.get('dates', '').strip()
    location = request.form.get('location', '').strip()

    # Валидация на пустые поля
    if not name or not dates or not location:
        return "Ошибка: Все поля должны быть заполнены", 400

    new_trip = Trip(name=name, dates=dates, location=location)
    db.session.add(new_trip)
    db.session.commit()
    return redirect(url_for('main.index'))

# 3. Детальная страница поездки + управление её чек-листом
@main_bp.route('/trip/<int:trip_id>', methods=['GET', 'POST'])
def trip_detail(trip_id):
    # Исправлено: используем правильный метод Flask-SQLAlchemy для автоматического вызова 404
    trip = db.first_or_404(db.select(Trip).filter_by(id=trip_id))

    if request.method == 'POST':
        # Добавление новой вещи в чек-лист
        item_name = request.form.get('item_name', '').strip()
        if not item_name:
            return "Название вещи не может быть пустым", 400
        
        new_item = Item(name=item_name, trip_id=trip.id)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('main.trip_detail', trip_id=trip.id))

    # Считаем статус готовности (X из Y вещей собрано)
    total_items = len(trip.items)
    packed_items = sum(1 for item in trip.items if item.is_packed)

    return render_template('trip.html', trip=trip, total_items=total_items, packed_items=packed_items)

# Изменение статуса вещи (собрано/не собрано)
@main_bp.route('/item/<int:item_id>/toggle', methods=['POST'])
def toggle_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        return "Вещь не найдена", 404
    item.is_packed = not item.is_packed
    db.session.commit()
    return redirect(url_for('main.trip_detail', trip_id=item.trip_id))

# 4. Редактирование и удаление поездки
@main_bp.route('/trip/<int:trip_id>/edit', methods=['GET', 'POST'])
def edit_trip(trip_id):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return "Поездка не найдена", 404

    if request.method == 'POST':
        trip.name = request.form.get('name', '').strip()
        trip.dates = request.form.get('dates', '').strip()
        trip.location = request.form.get('location', '').strip()
        
        if not trip.name or not trip.dates or not trip.location:
            return "Ошибка: Все поля должны быть заполнены", 400
            
        db.session.commit()
        return redirect(url_for('main.trip_detail', trip_id=trip.id))

    return render_template('edit_trip.html', trip=trip)

@main_bp.route('/trip/<int:trip_id>/delete', methods=['POST'])
def delete_trip(trip_id):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return "Поездка не найдена", 404
    db.session.delete(trip)
    db.session.commit()
    return redirect(url_for('main.index'))

# Творческое требование: Копирование чек-листа из другой поездки
@main_bp.route('/trip/<int:trip_id>/copy-template', methods=['POST'])
def copy_template(trip_id):
    target_trip = db.session.get(Trip, trip_id)
    from_trip_id = request.form.get('from_trip_id')
    
    if not target_trip or not from_trip_id:
        return "Неверные данные", 400
        
    source_trip = db.session.get(Trip, from_trip_id)
    if source_trip:
        for item in source_trip.items:
            # Копируем только названия вещей, сбрасывая галочки
            new_item = Item(name=item.name, trip_id=target_trip.id, is_packed=False)
            db.session.add(new_item)
        db.session.commit()
        
    return redirect(url_for('main.trip_detail', trip_id=target_trip.id))