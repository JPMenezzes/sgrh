from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    nome = db.Column(db.String(120), nullable=False)


class Profissao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)

    def __init__(self, nome, status):
        self.nome = nome
        self.status = status


class Pessoa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False, unique=True)
    profissao_id = db.Column(db.Integer, db.ForeignKey('profissao.id'), nullable=False)
    endereco = db.Column(db.String(150), nullable=False)

    profissao = db.relationship('Profissao', backref='pessoas', lazy=True)

    def __init__(self, nome, cpf, profissao_id, endereco):
        self.nome = nome
        self.cpf = cpf
        self.profissao_id = profissao_id
        self.endereco = endereco


class FolhaPagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    salario = db.Column(db.Float, nullable=False, default=0.0)
    comissao = db.Column(db.Float, nullable=False, default=0.0)
    descontos = db.Column(db.Float, nullable=False, default=0.0)
    gratificacoes = db.Column(db.Float, nullable=False, default=0.0)
    data_pagamento = db.Column(db.Date, nullable=False)

    pessoa = db.relationship('Pessoa', backref='folhas_pagamento', lazy=True)

    def __init__(self, pessoa_id, salario, comissao, descontos, gratificacoes, data_pagamento):
        self.pessoa_id = pessoa_id
        self.salario = salario
        self.comissao = comissao
        self.descontos = descontos
        self.gratificacoes = gratificacoes
        self.data_pagamento = data_pagamento
