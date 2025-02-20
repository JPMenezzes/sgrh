from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.senha, senha):
                flash('Logado com sucesso!', 'success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Senha incorreta!', 'error')
        else:
            flash('Email inexistente!', 'error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        nome = request.form['nome']
        senha1 = request.form['senha1']
        senha2 = request.form['senha2']

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email já cadastrado!", category='error')
        elif len(email) <= 4:
            flash('Email deve ser maior que 4 caracteres.', category='error')
        elif len(nome) <= 2:
            flash('Nome deve ser maior que 2 caracteres.', category='error')
        elif senha1 != senha2:
            flash('Senhas devem ser iguais.', category='error')
        elif len(senha1) <= 7:
            flash('A senha deve conter mais de 7 cacteres.', category='error')
        else:
            new_user = User(email=email, nome=nome, senha=generate_password_hash(senha1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Conta criada!', category='sucess')
            return redirect(url_for('auth.login'))

    return render_template("register.html", user=current_user)
