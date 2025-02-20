from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from . import db

from website.models import Pessoa, Profissao, FolhaPagamento

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


#CRUD -> Pessoa


@views.route('/cadastrar/pessoa', methods=['GET', 'POST'])
@login_required
def cadastrar_pessoa():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        profissao_id = request.form['profissao_id']
        endereco = request.form['endereco']

        profissao = Profissao.query.filter_by(id=profissao_id).first()
        if not profissao:
            flash("Profissão inválida.", category="error")
            return render_template("form_pessoa.html", user=current_user)

        if not nome or not cpf or not profissao_id or not endereco:
            flash("Todos os campos são obrigatórios.", category="error")
        elif len(cpf) != 11 or not cpf.isdigit():
            flash("CPF inválido.", category="error")
        elif Pessoa.query.filter_by(cpf=cpf).first():
            flash("CPF já cadastrado.", category="error")
        else:
            new_pessoa = Pessoa(nome, cpf, profissao_id, endereco)
            db.session.add(new_pessoa)
            db.session.commit()
            flash("Pessoa cadastrada com sucesso!", category="success")
            return redirect(url_for('views.home'))

    profissoes = Profissao.query.all()
    return render_template("forms/form_pessoa.html", profissoes=profissoes, user=current_user)


@views.route('/listar/pessoa', methods=['GET'])
@login_required
def listar_pessoa():
    pessoas = Pessoa.query.options(joinedload(Pessoa.profissao)).all()
    return render_template("list/list_pessoa.html", pessoas=pessoas, user=current_user)


@views.route('/editar/pessoa/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_pessoa(id):
    pessoa = Pessoa.query.get(id)

    if not pessoa:
        flash("Pessoa não encontrada.", category="error")
        return redirect(url_for('views.listar_pessoa'))

    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        profissao_id = request.form['profissao_id']
        endereco = request.form['endereco']

        profissao = Profissao.query.filter_by(id=profissao_id).first()
        if not profissao:
            flash("Profissão inválida.", category="error")
            return render_template("forms/form_pessoa.html", pessoa=pessoa, user=current_user)

        if not nome or not cpf or not endereco:
            flash("Todos os campos são obrigatórios.", category="error")
        elif len(cpf) != 11 or not cpf.isdigit():
            flash("CPF inválido.", category="error")
        else:
            pessoa.nome = nome
            pessoa.cpf = cpf
            pessoa.profissao_id = profissao_id
            pessoa.endereco = endereco

            db.session.commit()
            flash("Pessoa atualizada com sucesso!", category="success")
            return redirect(url_for('views.listar_pessoa'))

    return render_template("forms/form_pessoa.html", pessoa=pessoa, profissoes=Profissao.query.all(), user=current_user)


@views.route('/deletar/pessoa/<int:id>', methods=['POST'])
@login_required
def deletar_pessoa(id):
    pessoa = Pessoa.query.get(id)

    if not pessoa:
        flash("Pessoa não encontrada.", category="error")
        return redirect(url_for('views.listar_pessoa'))

    if pessoa.folhas_pagamento:
        flash("Não é possível excluir uma pessoa com folha de pagamento associada.", category="error")
        return redirect(url_for('views.listar_pessoa'))

    db.session.delete(pessoa)
    db.session.commit()
    flash("Pessoa excluída com sucesso!", category="success")
    return redirect(url_for('views.listar_pessoa'))


#CRUD -> Profissao


@views.route('/cadastrar/profissao', methods=['GET', 'POST'])
@login_required
def cadastrar_profissao():
    if request.method == 'POST':
        nome = request.form['nome']
        status = request.form['status']
        if not nome or not status:
            flash("Todos os campos são obrigatórios.", category="error")
        elif Profissao.query.filter_by(nome=nome).first():
            flash("Profissão já cadastrada.", category="error")
        else:
            new_profissao = Profissao(nome, status)
            db.session.add(new_profissao)
            db.session.commit()
            flash("Profissão cadastrada com sucesso!", category="success")
            return redirect(url_for('views.home'))

    return render_template("forms/form_profissao.html", user=current_user)


@views.route('/listar/profissao', methods=['GET'])
@login_required
def listar_profissao():
    profissoes = Profissao.query.all()
    return render_template("list/list_profissao.html", profissoes=profissoes, user=current_user)


@views.route('/editar/profissao/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_profissao(id):
    profissao = Profissao.query.get(id)

    if not profissao:
        flash("Profissão não encontrada.", category="error")
        return redirect(url_for('views.listar_profissao'))

    if request.method == 'POST':
        nome = request.form['nome']
        status = request.form['status']

        if not nome or not status:
            flash("Todos os campos são obrigatórios.", category="error")
        else:
            profissao.nome = nome
            profissao.status = status

            db.session.commit()
            flash("Profissão atualizada com sucesso!", category="success")
            return redirect(url_for('views.listar_profissao'))

    return render_template("forms/form_profissao.html", profissao=profissao, user=current_user)


@views.route('/deletar/profissao/<int:id>', methods=['POST'])
@login_required
def deletar_profissao(id):
    profissao = Profissao.query.get(id)

    if not profissao:
        flash("Profissão não encontrada.", category="error")
        return redirect(url_for('views.listar_profissao'))

    if profissao.pessoas:
        flash("Não é possível excluir uma profissão com pessoas associadas.", category="error")
        return redirect(url_for('views.listar_profissao'))

    db.session.delete(profissao)
    db.session.commit()
    flash("Profissão excluída com sucesso!", category="success")
    return redirect(url_for('views.listar_profissao'))


#CRUD -> Folha de Pagamento


@views.route('/cadastrar/folha-pagamento', methods=['GET', 'POST'])
@login_required
def cadastrar_folha_pagamento():
    if request.method == 'POST':
        pessoa_id = request.form['pessoa_id']
        salario = request.form['salario']
        comissao = request.form['comissao']
        descontos = request.form['descontos']
        gratificacoes = request.form['gratificacoes']
        data_pagamento = request.form['data_pagamento']

        pessoa = Pessoa.query.filter_by(id=pessoa_id).first()
        if not pessoa:
            flash("Pessoa inválida.", category="error")
            return render_template("form_pagamento.html", user=current_user)

        if not pessoa_id or not salario or not descontos or not data_pagamento:
            flash("Os campos pessoa, salário, descontos e data de pagamanto são obrigatórios.", category="error")
            return render_template("form_pagamento.html", user=current_user)

        try:
            salario = float(salario)
            comissao = float(comissao)
            descontos = float(descontos)
            gratificacoes = float(gratificacoes)
        except ValueError:
            flash("Salário, comissão, descontos e gratificações devem ser números válidos.", category="error")
            return render_template("form_pagamento.html", user=current_user)

        try:
            data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
        except ValueError:
            flash("Data de pagamento inválida. Use o formato YYYY-MM-DD.", category="error")
            return render_template("form_pagamento.html", user=current_user)

        new_folha_pagamento = FolhaPagamento(pessoa_id, salario, comissao, descontos, gratificacoes, data_pagamento)

        db.session.add(new_folha_pagamento)
        db.session.commit()
        flash("Folha de pagamento cadastrada com sucesso!", category="success")
        return redirect(url_for('views.home'))

    pessoas = Pessoa.query.all()
    return render_template("forms/form_pagamento.html", pessoas=pessoas, user=current_user)


@views.route('/listar/folha-pagamento', methods=['GET'])
@login_required
def listar_folha_pagamento():
    pagamentos = FolhaPagamento.query.options(joinedload(FolhaPagamento.pessoa)).all()
    return render_template("list/list_pagamento.html", pagamentos=pagamentos, user=current_user)


@views.route('/editar/folha-pagamento/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_folha_pagamento(id):
    folha_pagamento = FolhaPagamento.query.get(id)

    if not folha_pagamento:
        flash("Folha de pagamento não encontrada.", category="error")
        return redirect(url_for('views.listar_folha_pagamento'))

    if request.method == 'POST':
        pessoa_id = request.form['pessoa_id']
        salario = request.form['salario']
        comissao = request.form['comissao']
        descontos = request.form['descontos']
        gratificacoes = request.form['gratificacoes']
        data_pagamento = request.form['data_pagamento']

        pessoa = Pessoa.query.get(pessoa_id)
        if not pessoa:
            flash("Pessoa inválida.", category="error")
            return redirect(url_for('views.listar_folha_pagamento'))

        if not pessoa_id or not salario or not descontos or not data_pagamento:
            flash("Os campos pessoa, salário, descontos e data de pagamanto são obrigatórios.", category="error")
        else:
            try:
                data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
            except ValueError:
                flash("Data de pagamento inválida. Use o formato YYYY-MM-DD.", category="error")
                return render_template("form_pagamento.html", user=current_user)

            folha_pagamento.pessoa_id = pessoa_id
            folha_pagamento.salario = salario
            folha_pagamento.comissao = comissao
            folha_pagamento.descontos = descontos
            folha_pagamento.gratificacoes = gratificacoes
            folha_pagamento.data_pagamento = data_pagamento

            db.session.commit()
            flash("Folha de pagamento atualizada com sucesso!", category="success")
            return redirect(url_for('views.listar_folha_pagamento'))

    return render_template("forms/form_pagamento.html", folha=folha_pagamento, pessoas=Pessoa.query.all(),
                           user=current_user)


@views.route('/deletar/folha-pagamento/<int:id>', methods=['POST'])
@login_required
def deletar_folha_pagamento(id):
    folha_pagamento = FolhaPagamento.query.get(id)

    if not folha_pagamento:
        flash("Folha de pagamento não encontrada.", category="error")
        return redirect(url_for('views.listar_folha_pagamento'))

    db.session.delete(folha_pagamento)
    db.session.commit()
    flash("Folha de pagamento deletada com sucesso!", category="success")
    return redirect(url_for('views.listar_folha_pagamento'))


