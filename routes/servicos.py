from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Despesa, Veiculo, Prestador
import math

despesas_bp = Blueprint('servicos', __name__, url_prefix='/servicos')

@despesas_bp.route('/', methods=['GET', 'POST'])
def listar_despesas():
    if request.method == 'POST':
        page = request.form.get('page', 1)
        search = request.form.get('search', '')
    else:
        page = request.args.get('page', 1)
        search = request.args.get('search', '')

    query = db.session.query(Despesa).join(Veiculo, Despesa.idplaca == Veiculo.idplaca).join(Prestador, Despesa.idprestador == Prestador.idprestador).add_columns(
        Despesa.iddespesa, Despesa.descricao, Despesa.data_servico, Despesa.valor, Veiculo.idplaca, Prestador.nome_empresa
    ).order_by(Despesa.data_servico.desc())

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



@despesas_bp.route('/novo', methods=['GET', 'POST'])
def nova_despesa():
    if request.method == 'POST':
        nova_despesa = Despesa(
            descricao=request.form['descricao'],
            data_servico=request.form['data_servico'],
            valor=request.form['valor'],
            idplaca=request.form['idplaca'],
            idprestador=request.form['idprestador']
        )
        db.session.add(nova_despesa)
        db.session.commit()
        flash('Despesa adicionada com sucesso!', 'success')
        return redirect(url_for('servicos.listar_despesas'))
    veiculos = db.session.query(Veiculo).all()
    prestadores = db.session.query(Prestador).all()
    return render_template('servicos/form_servicos.html', veiculos=veiculos, prestadores=prestadores)

@despesas_bp.route('/editar/<int:iddespesa>', methods=['GET', 'POST'])
def editar_despesa(iddespesa):
    despesa = db.session.query(Despesa).filter_by(iddespesa=iddespesa).first()
    if request.method == 'POST':
        despesa.descricao = request.form['descricao']
        despesa.data_servico = request.form['data_servico']
        despesa.valor = request.form['valor']
        despesa.idplaca = request.form['idplaca']
        despesa.idprestador = request.form['idprestador']
        db.session.commit()
        flash('Despesa atualizada com sucesso!', 'success')
        return redirect(url_for('servicos.listar_despesas'))
    veiculos = db.session.query(Veiculo).all()
    prestadores = db.session.query(Prestador).all()
    return render_template('servicos/form_servicos.html', despesa=despesa, veiculos=veiculos, prestadores=prestadores)

@despesas_bp.route('/excluir/<int:iddespesa>', methods=['POST'])
def excluir_despesa(iddespesa):
    despesa = db.session.query(Despesa).filter_by(iddespesa=iddespesa).first()
    db.session.delete(despesa)
    db.session.commit()
    flash('Despesa excluída com sucesso!', 'success')
    return redirect(url_for('servicos.listar_despesas'))

@despesas_bp.route('/excluir_selecionados', methods=['POST'])
def excluir_selecionados():
    ids = request.form.getlist('ids')
    for iddespesa in ids:
        despesa = db.session.query(Despesa).filter_by(iddespesa=iddespesa).first()
        db.session.delete(despesa)
    db.session.commit()
    flash('Despesas selecionadas excluídas com sucesso!', 'success')
    return redirect(url_for('servicos.listar_despesas'))
