from flask import Flask, request, render_template, redirect, url_for, flash,jsonify, session, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from database import db
from functools import wraps
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123'
# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://admin:123456789@DESKTOP-V6MD99V\MSSQLSERVER1/Cinema?driver=SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from models import Film, Hall, Showtime, Ticket, User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Эта страница требует входа в систему.')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/test-db')
@login_required
def test_db():
    try:
        # Попытка получить количество фильмов из базы данных
        film_count = Film.query.count()
        return f"Количество фильмов в базе данных: {film_count}"
    except SQLAlchemyError as e:
        # В случае ошибки подключения к базе данных
        return f"Ошибка подключения к базе данных: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Необходимо ввести имя пользователя и пароль')
            return redirect(url_for('login'))

            # Поиск пользователя в базе данных
        user = User.query.filter_by(username=username).first()

        # Проверка, существует ли пользователь и верен ли пароль
        if user and user.password_hash == password:
            session['logged_in'] = True
            session['username'] = username
            next_page = request.args.get('next')
            # Пароль верный, переход на домашнюю страницу
            return redirect(next_page or url_for('home'))
        else:
            # Пользователь не найден или пароль неверный
            flash('Такого пользователя не существует или неверный пароль')
            return redirect(url_for('login'))

    # Показать форму входа при GET-запросе
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')

        if password != confirm_password:
            flash('Пароли не совпадают. Попробуйте снова.')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None:
            flash('Пользователь с таким именем уже существует.')
            return redirect(url_for('register'))

        # Создание нового пользователя
        new_user = User(username=username)
        new_user.password_hash = password
        new_user.Email = email

        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно. Теперь вы можете войти.')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Вы вышли из системы.')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/filmNow')
def film_now():
    # Запрос к базе данных для получения всех фильмов, которые идут в прокате
    films_in_show = Showtime.query.join(Film, Showtime.FilmID == Film.FilmID).all()

    # Передача результатов в шаблон
    return render_template('film_now.html', films=films_in_show)




if __name__ == "__main__":
    app.run(port=5001, debug=True)