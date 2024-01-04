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
        film_count = Film.query.count()
        return f"Количество фильмов в базе данных: {film_count}"
    except SQLAlchemyError as e:
        return f"Ошибка подключения к базе данных: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Необходимо ввести имя пользователя и пароль')
            return redirect(url_for('login'))

            # Поиск пользователя в бд
        user = User.query.filter_by(username=username).first()

        # Проверка
        if user and user.password_hash == password:
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user.UserID  
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Такого пользователя не существует или неверный пароль')
            return redirect(url_for('login'))

    # при GET-запросе
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
@login_required
def film_now():
    films_in_show = Showtime.query.join(Film, Showtime.FilmID == Film.FilmID).all()
    
    # for showtime in films_in_show:
    #     assert 'ShowtimeID' in dir(showtime), "Объект Showtime не содержит ShowtimeID"
    
    return render_template('film_now.html', films=films_in_show)

def get_current_user_id():
    return session.get('user_id')

@app.route('/buy-ticket/<int:showtime_id>', methods=['GET', 'POST'])
@login_required
def buy_ticket(showtime_id):
    current_user_id = get_current_user_id()  
    showtime = Showtime.query.get_or_404(showtime_id)

    taken_seats = Ticket.query.with_entities(Ticket.SeatNumber).filter_by(ShowtimeID=showtime_id).all()
    taken_seats = [seat.SeatNumber for seat in taken_seats]

    
    total_seats = 20  
    seats = [{'number': i, 'is_taken': i in taken_seats} for i in range(1, total_seats + 1)]

    if request.method == 'POST':
        seat_number = int(request.form.get('seat_number'))

        # Проверка
        if seat_number in taken_seats:
            flash('Это место уже занято.')
            return redirect(url_for('buy_ticket', showtime_id=showtime_id))

        new_ticket = Ticket(ShowtimeID=showtime_id, SeatNumber=seat_number,Price =10, UserId=current_user_id, Status='Куплено')
        db.session.add(new_ticket)
        db.session.commit()

        flash('Билет успешно куплен!')

    return render_template('buy_ticket.html', seats=seats, showtime_id=showtime_id)


    

if __name__ == "__main__":
    app.run(port=5001, debug=True)