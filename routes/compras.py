from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Compra, Cliente, Veiculo
import math
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

@compras_bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'POST':
        page = request.form.get('page', 1)
        search = request.form.get('search', '')
    else:
        page = request.args.get('page', 1)
        search = request.args.get('search', '')

    query = db.session.query(Compra).join(Veiculo, Compra.idplaca == Veiculo.idplaca).join(Cliente, Compra.idcliente == Cliente.idcliente).add_columns(
        Compra.idcompra, 
        Compra.data, 
        Compra.valor_pago, 
        Compra.forma_pagamento, 
        Veiculo.idplaca, 
        Cliente.nome
    ).order_by(Compra.data.desc())

    query = query.add_columns(
        db.func.replace(db.func.replace(db.func.replace(db.func.to_char(Compra.valor_pago, 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.').label('formatted_valor_pago'),
    )

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Cliente.nome.ilike(f"%{term}%"))
            
    total = query.count()
    max_pages = math.ceil(total / 10)
    showing = 10 if int(page) < max_pages else (total - 10 * (int(page) - 1)) % 10
    array = query.offset((int(page) - 1) * 10).limit(10).all()

    return render_template('compras/compras.html',
                            title='Compras', context='compras',
                            array=array, total=total, page=page, search=search, max_pages=max_pages, showing=showing)


@compras_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        idplaca_str = request.form['idplaca']
        idcliente_str = request.form['idcliente']

        veiculo = db.session.query(Veiculo).filter(Veiculo.idplaca == idplaca_str.split()[-1].strip('<>')).first()
        cliente = db.session.query(Cliente).filter(Cliente.idcliente == int(idcliente_str.split()[-1].strip('<>'))).first()
        
        idcompra = db.session.query(db.func.max(Compra.idcompra)).scalar()
        idcompra = (idcompra + 1) if idcompra is not None else 1

        if veiculo and cliente:
            new_purchase = Compra(
                idcompra=idcompra,
                data=request.form['data'],
                valor_pago=request.form['valor_pago'],
                forma_pagamento=request.form['forma_pagamento'],
                idplaca=veiculo.idplaca,
                idcliente=cliente.idcliente
            )
            db.session.add(new_purchase)
            db.session.commit()
            flash('Compra adicionada com sucesso!', 'success')
            return redirect(url_for('compras.list'))
        else:
            flash('Erro ao adicionar compra: Veículo ou Cliente não encontrado.', 'danger')
            return redirect(url_for('compras.add'))

    veiculos = db.session.query(Veiculo).all()
    clientes = db.session.query(Cliente).all()
    return render_template('compras/form_compras.html', titulo='Nova compra', veiculos=veiculos, clientes=clientes, datetime=datetime.now().strftime('%Y-%m-%d'))

@compras_bp.route('/edit/<int:idcompra>', methods=['GET', 'POST'])
def edit(idcompra):
    compra = db.session.query(Compra).filter_by(idcompra=idcompra).first()
    if request.method == 'POST':
        compra.data = request.form['data']
        compra.valor_pago = request.form['valor_pago']
        compra.forma_pagamento = request.form['forma_pagamento']
        compra.idplaca = request.form['idplaca']
        compra.idcliente = request.form['idcliente']

        db.session.commit()
        flash('Compra atualizada com sucesso!', 'success')
        return redirect(url_for('compras.list'))
    veiculos = db.session.query(Veiculo).all()
    clientes = db.session.query(Cliente).all()
    return render_template('compras/form_compras.html', compra=compra, veiculos=veiculos, clientes=clientes)

@compras_bp.route('/delete/<int:idcompra>', methods=['POST'])
def delete(idcompra):
    compra = db.session.query(Compra).filter_by(idcompra=idcompra).first()
    db.session.delete(compra)
    db.session.commit()
    flash('Compra excluída com sucesso!', 'success')
    return redirect(url_for('compras.list'))

@compras_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    ids = request.form.getlist('ids')
    for idcompra in ids:
        compra = db.session.query(Compra).filter_by(idcompra=idcompra).first()
        db.session.delete(compra)
    db.session.commit()
    flash('Compras selecionadas excluídas com sucesso!', 'success')
    return redirect(url_for('compras.list'))
