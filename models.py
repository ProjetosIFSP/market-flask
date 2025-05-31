from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DECIMAL, Date, ForeignKey

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'cliente'

    idcliente = Column(Integer, primary_key=True)
    nome = Column(String(60))
    endereco = Column(String(255))
    cidade = Column(String(80))
    uf = Column(String(2))
    cep = Column(String(9))

class Veiculo(db.Model):
    __tablename__ = 'veiculo'

    idplaca = Column(String(9), primary_key=True)
    ano = Column(Integer, nullable=False)
    modelo = Column(Integer, nullable=False)
    preco_fipe = Column(DECIMAL(10, 2))
    fabricante = Column(String(50))
    modelo_veiculo = Column(String(60))
    cor = Column(String(20))
    preco_venda = Column(DECIMAL(10, 2))
    total_despesa = Column(DECIMAL(10, 2))

class Venda(db.Model):
    __tablename__ = 'venda'

    idvenda = Column(Integer, primary_key=True)
    data = Column(Date)
    valor_vendido = Column(DECIMAL(10, 2))
    idcliente = Column(Integer, ForeignKey('cliente.idcliente'))
    idplaca = Column(String(9), ForeignKey('veiculo.idplaca'))
    forma_pagamento = Column(String(40))

class Compra(db.Model):
    __tablename__ = 'compra'

    idcompra = Column(Integer, primary_key=True)
    idplaca = Column(String(9), ForeignKey('veiculo.idplaca'))
    idcliente = Column(Integer, ForeignKey('cliente.idcliente'))
    data = Column(Date)
    valor_pago = Column(DECIMAL(10, 2))
    forma_pagamento = Column(String(40))

class Prestador(db.Model):
    __tablename__ = 'prestador'

    idprestador = Column(Integer, primary_key=True)
    nome_empresa = Column(String(60))
    cidade = Column(String(80))
    uf = Column(String(2))
    cep = Column(String(9))

class Despesa(db.Model):
    __tablename__ = 'despesa'

    iddespesa = Column(Integer, primary_key=True)
    idplaca = Column(String(9), ForeignKey('veiculo.idplaca'))
    descricao = Column(String(80))
    valor = Column(DECIMAL(10, 2))
    idprestador = Column(Integer, ForeignKey('prestador.idprestador'))
    data_servico = Column(Date)
