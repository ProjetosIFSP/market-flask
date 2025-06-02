from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Venda, Cliente, Veiculo
import math
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

vendas_bp = Blueprint('vendas', __name__, url_prefix='/vendas')

@vendas_bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'POST':
        page = request.form.get('page', 1)
        search = request.form.get('search', '')
    else:
        page = request.args.get('page', 1)
        search = request.args.get('search', '')

    query = db.session.query(Venda).join(Veiculo, Venda.idplaca == Veiculo.idplaca).join(Cliente, Venda.idcliente == Cliente.idcliente).add_columns(
        Venda.idvenda, 
        Venda.data, 
        Venda.valor_vendido, 
        Venda.forma_pagamento, 
        Veiculo.idplaca, 
        Cliente.nome
    ).order_by(Venda.data.desc())

    query = query.add_columns(
        db.func.replace(db.func.replace(db.func.replace(db.func.to_char(Venda.valor_vendido, 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.').label('formatted_valor_vendido'),
    )

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Cliente.nome.ilike(f"%{term}%"))
            
    total = query.count()
    max_pages = math.ceil(total / 10)
    showing = 10 if int(page) < max_pages else (total - 10 * (int(page) - 1)) % 10
    array = query.offset((int(page) - 1) * 10).limit(10).all()

    return render_template('vendas/vendas.html',
                            title='Vendas', context='vendas',
                            array=array, total=total, page=page, search=search, max_pages=max_pages, showing=showing)


@vendas_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        idplaca_str = request.form['idplaca']
        idcliente_str = request.form['idcliente']

        veiculo = db.session.query(Veiculo).filter(Veiculo.idplaca == idplaca_str.split()[-1].strip('<>')).first()
        cliente = db.session.query(Cliente).filter(Cliente.idcliente == int(idcliente_str.split()[-1].strip('<>'))).first()
        
        idvenda = db.session.query(db.func.max(Venda.idvenda)).scalar()
        idvenda = (idvenda + 1) if idvenda is not None else 1

        if veiculo and cliente:
            new_sale = Venda(
                idvenda=idvenda,
                data=request.form['data'],
                valor_vendido=request.form['valor_vendido'],
                forma_pagamento=request.form['forma_pagamento'],
                idplaca=veiculo.idplaca,
                idcliente=cliente.idcliente
            )
            db.session.add(new_sale)
            db.session.commit()
            flash('Venda adicionada com sucesso!', 'success')
            return redirect(url_for('vendas.list'))
        else:
            flash('Erro ao adicionar venda: Veículo ou Cliente não encontrado.', 'danger')
            return redirect(url_for('vendas.add'))

    veiculos = db.session.query(Veiculo).filter(~Veiculo.idplaca.in_(
      db.session.query(Venda.idplaca).distinct()
    )).all()
    clientes = db.session.query(Cliente).all()
    return render_template('vendas/form_vendas.html', titulo='Nova venda', veiculos=veiculos, clientes=clientes, datetime=datetime.now().strftime('%Y-%m-%d'))

@vendas_bp.route('/edit/<int:idvenda>', methods=['GET', 'POST'])
def edit(idvenda):
    venda = db.session.query(Venda).filter_by(idvenda=idvenda).first()
    if request.method == 'POST':
        venda.data = request.form['data']
        venda.valor_vendido = request.form['valor_vendido']
        venda.forma_pagamento = request.form['forma_pagamento']
        venda.idplaca = request.form['idplaca']
        venda.idcliente = request.form['idcliente']

        db.session.commit()
        flash('Venda atualizada com sucesso!', 'success')
        return redirect(url_for('vendas.list'))
    veiculos = db.session.query(Veiculo).all()
    clientes = db.session.query(Cliente).all()
    return render_template('vendas/form_vendas.html', venda=venda, veiculos=veiculos, clientes=clientes)

@vendas_bp.route('/delete/<int:idvenda>', methods=['POST'])
def delete(idvenda):
    venda = db.session.query(Venda).filter_by(idvenda=idvenda).first()
    db.session.delete(venda)
    db.session.commit()
    flash('Venda excluída com sucesso!', 'success')
    return redirect(url_for('vendas.list'))

@vendas_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    ids = request.form.getlist('ids')
    for idvenda in ids:
        venda = db.session.query(Venda).filter_by(idvenda=idvenda).first()
        db.session.delete(venda)
    db.session.commit()
    flash('Vendas selecionadas excluídas com sucesso!', 'success')
    return redirect(url_for('vendas.list'))
