from flask import Blueprint, json, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Despesa, Veiculo, Prestador
import math
from datetime import datetime

despesas_bp = Blueprint('servicos', __name__, url_prefix='/servicos')

@despesas_bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'POST':
        page = request.form.get('page', 1)
        search = request.form.get('search', '')
    else:
        page = request.args.get('page', 1)
        search = request.args.get('search', '')

    query = db.session.query(Despesa).join(Veiculo, Despesa.idplaca == Veiculo.idplaca).join(Prestador, Despesa.idprestador == Prestador.idprestador).add_columns(
        Despesa.iddespesa, 
        Despesa.descricao, 
        Despesa.data_servico, 
        Despesa.valor, 
        Veiculo.idplaca, 
        Prestador.nome_empresa
    ).order_by(Despesa.data_servico.desc())

    query = query.add_columns(
        db.func.replace(db.func.replace(db.func.replace(db.func.to_char(Despesa.valor, 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.').label('formatted_valor'),
    )

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Prestador.nome_empresa.ilike(f"%{term}%"))
            
    total = query.count()
    max_pages = math.ceil(total / 10)
    showing = 10 if int(page) < max_pages else (total - 10 * (int(page) - 1)) % 10
    array = query.offset((int(page) - 1) * 10).limit(10).all()

    return render_template('servicos/servicos.html',
                            title='Serviços', context='servicos',
                            array=array, total=total, page=page, search=search, max_pages=max_pages, showing=showing)

@despesas_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        print(json.dumps(request.form))

        idplaca_str = request.form['idplaca']
        idprestador_str = request.form['idprestador']

        veiculo = db.session.query(Veiculo).filter(Veiculo.idplaca == idplaca_str.split()[-1].strip('<>')).first()
        prestador = db.session.query(Prestador).filter(Prestador.idprestador == int(idprestador_str.split()[-1].strip('<>'))).first()
        
        iddespesa = db.session.query(db.func.max(Despesa.iddespesa)).scalar()
        iddespesa = (iddespesa + 1) if iddespesa is not None else 1

        if veiculo and prestador:
            new_expense = Despesa(
                iddespesa=iddespesa,
                descricao=request.form['descricao'],
                data_servico=request.form['data_servico'],
                valor=request.form['valor'],
                idplaca=veiculo.idplaca,
                idprestador=prestador.idprestador
            )
            db.session.add(new_expense)
            db.session.commit()
            flash('Despesa adicionada com sucesso!', 'success')
            return redirect(url_for('servicos.list'))
        else:
            flash('Erro ao adicionar despesa: Veículo ou Prestador não encontrado.', 'danger')
            return redirect(url_for('servicos.add'))

    veiculos = db.session.query(Veiculo).all()
    prestadores = db.session.query(Prestador).all()
    return render_template('servicos/form_servicos.html', title='Novo serviço', veiculos=veiculos, prestadores=prestadores, datetime=datetime.now().strftime('%Y-%m-%d'))

@despesas_bp.route('/edit/<int:iddespesa>', methods=['GET', 'POST'])
def edit(iddespesa):
    despesa = db.session.query(Despesa).filter_by(iddespesa=iddespesa).first()
    if request.method == 'POST':
        despesa.descricao = request.form['descricao']
        despesa.data_servico = request.form['data_servico']
        despesa.valor = request.form['valor']
        despesa.idplaca = request.form['idplaca']
        despesa.idprestador = request.form['idprestador']


        db.session.commit()
        flash('Despesa atualizada com sucesso!', 'success')
        return redirect(url_for('servicos.list'))
    veiculos = db.session.query(Veiculo).all()
    prestadores = db.session.query(Prestador).all()
    return render_template('servicos/form_servicos.html', despesa=despesa, veiculos=veiculos, prestadores=prestadores)

@despesas_bp.route('/delete/<int:iddespesa>', methods=['POST'])
def delete(iddespesa):
    despesa = db.session.query(Despesa).filter_by(iddespesa=iddespesa).first()
    db.session.delete(despesa)
    db.session.commit()
    flash('Despesa excluída com sucesso!', 'success')
    return redirect(url_for('servicos.list'))

@despesas_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    ids = request.form.getlist('ids')
    for iddespesa in ids:
        despesa = db.session.query(Despesa).filter_by(iddespesa=iddespesa).first()
        db.session.delete(despesa)
    db.session.commit()
    flash('Despesas selecionadas excluídas com sucesso!', 'success')
    return redirect(url_for('servicos.list'))
