import pytest
from app import create_app, db
from app.models import Trip, Item

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

#Тест главной страницы
def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

#Тест добавления объекта
def test_add_trip(client, app):
    response = client.post('/trip/add', data={
        'name': 'Летний Сочи',
        'dates': '01.07-10.07',
        'location': 'Сочи'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    with app.app_context():
        trip = Trip.query.filter_by(name='Летний Сочи').first()
        assert trip is not None
        assert trip.location == 'Сочи'

#Тест поиска
def test_search_filtration(client, app):
    with app.app_context():
        t1 = Trip(name='Поездка 1', dates='1-2', location='Алтай')
        t2 = Trip(name='Поездка 2', dates='3-4', location='Байкал')
        db.session.add_all([t1, t2])
        db.session.commit()

    # Ищем Алтай
    response = client.get('/?search=Алтай')
    html = response.data.decode('utf-8')
    assert 'Алтай' in html
    assert 'Байкал' not in html

#Тест обработки ошибки
def test_404_error(client):
    response = client.get('/trip/999')
    assert response.status_code == 404

#Тест на корректность данных
def test_validation_empty_fields(client, app):
    response = client.post('/trip/add', data={
        'name': '',  # Пустое поле названия
        'dates': '10-20.08',
        'location': 'Москва'
    })

    assert response.status_code == 400
    
    with app.app_context():
        assert Trip.query.count() == 0