from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'cliente'

    idcliente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60))
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(80))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(9))

class Veiculo(db.Model):
    __tablename__ = 'veiculo'

    idplaca = db.Column(db.String(9), primary_key=True)
    ano = db.Column(db.Integer)
    modelo = db.Column(db.Integer)
    preco_fipe = db.Column(db.DECIMAL(10, 2))
    fabricante = db.Column(db.String(50))
    modelo_veiculo = db.Column(db.String(60))
    cor = db.Column(db.String(20))
    preco_venda = db.Column(db.DECIMAL(10, 2))
    total_despesa = db.Column(db.DECIMAL(10, 2))
