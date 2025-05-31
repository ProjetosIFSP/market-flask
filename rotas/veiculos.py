from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Veiculo
import math

veiculos_bp = Blueprint('veiculos', __name__)

@veiculos_bp.route('/veiculos', methods=['GET', 'POST'])
def list_veiculos():
    if request.method == 'POST':
        page = request.form.get('page', 1)
        search = request.form.get('search', '')

        query = db.session.query(Veiculo).order_by(Veiculo.fabricante.asc())
        if search:
            search_terms = search.split()
            for term in search_terms:
                query = query.filter(Veiculo.fabricante.ilike(f"%{term}%"))

        total = query.count()
        max_pages = math.ceil(total / 10)
        showing = 10 if int(page) < max_pages else (total - 10 * (int(page) - 1)) % 10
        veiculos = query.offset((int(page) - 1) * 10).limit(10).all()

        return render_template('veiculos.html', veiculos=veiculos, total=total, page=int(page), search=search, max_pages=max_pages, showing=showing)

    page = request.args['page'] if 'page' in request.args else 1
    try:
        page = int(page)
    except ValueError:
        page = 1

    search = request.args['search'] if 'search' in request.args else ''
    query = db.session.query(Veiculo)
    query = query.order_by(Veiculo.fabricante.asc())

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Veiculo.fabricante.ilike(f"%{term}%"))

    total = query.count()
    max_pages = math.ceil(total / 10)
    showing = 10 if page < max_pages else (total - 10 * (page - 1)) % 10
    veiculos = query.offset((page - 1) * 10).limit(10).all()

    return render_template('veiculos.html', veiculos=veiculos, total=total, page=page, search=search, max_pages=max_pages, showing=showing)

@veiculos_bp.route('/veiculos/novo', methods=['GET', 'POST'])
def novo_veiculo():
    if request.method == 'POST':
        idplaca = request.form['idplaca']
        ano = request.form['ano']
        modelo = request.form['modelo']
        preco_fipe = request.form['preco_fipe']
        fabricante = request.form['fabricante']
        modelo_veiculo = request.form['modelo_veiculo']
        cor = request.form['cor']
        preco_venda = request.form['preco_venda']
        total_despesa = request.form['total_despesa']

        novo_veiculo = Veiculo(
            idplaca=idplaca,
            ano=ano,
            modelo=modelo,
            preco_fipe=preco_fipe,
            fabricante=fabricante,
            modelo_veiculo=modelo_veiculo,
            cor=cor,
            preco_venda=preco_venda,
            total_despesa=total_despesa
        )
        db.session.add(novo_veiculo)
        db.session.commit()

        flash('Veículo cadastrado com sucesso!', 'success')
        return redirect(url_for('veiculos.list_veiculos'))

    return render_template('form_veiculo.html', titulo='Novo veículo', action=url_for('novo_veiculo'))

@veiculos_bp.route('/veiculos/edit/<string:idplaca>', methods=['GET', 'POST'])
def edit_veiculo(idplaca):
    veiculo = db.session.query(Veiculo).filter_by(idplaca=idplaca).first()
    if not veiculo:
        flash('Veículo não encontrado!', 'error')
        return redirect(url_for('veiculos.list_veiculos'))

    if request.method == 'POST':
        veiculo.ano = request.form['ano']
        veiculo.modelo = request.form['modelo']
        veiculo.preco_fipe = request.form['preco_fipe']
        veiculo.fabricante = request.form['fabricante']
        veiculo.modelo_veiculo = request.form['modelo_veiculo']
        veiculo.cor = request.form['cor']
        veiculo.preco_venda = request.form['preco_venda']
        veiculo.total_despesa = request.form['total_despesa']

        db.session.commit()
        flash('Veículo atualizado com sucesso!', 'success')
        return redirect(url_for('veiculos.list_veiculos'))

    return render_template('form_veiculo.html', titulo='Alterando veículo', action=url_for('edit_veiculo', idplaca=idplaca), veiculo=veiculo)

@veiculos_bp.route('/veiculos/delete/<string:idplaca>', methods=['POST'])
def delete_veiculo(idplaca):
    veiculo = db.session.query(Veiculo).filter_by(idplaca=idplaca).first()

    if not veiculo:
        flash('Veículo não encontrado!', 'error')
        return redirect(url_for('veiculos.list_veiculos'))

    try:
        db.session.delete(veiculo)
        db.session.commit()
        flash('Veículo excluído com sucesso!', 'success')
    except Exception:
        flash('Erro ao excluir veículo. Tente novamente.', 'error')

    return redirect(url_for('veiculos.list_veiculos'))