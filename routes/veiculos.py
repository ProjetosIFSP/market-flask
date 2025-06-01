from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Veiculo
import math

veiculos_bp = Blueprint('veiculos', __name__, url_prefix='/veiculos')

@veiculos_bp.route('/', methods=['GET', 'POST'])
def list_veiculos():
    if request.method == 'POST':
        page = request.form.get('page', 1)
        search = request.form.get('search', '')
    else:
        page = request.args.get('page', 1)
        search = request.args.get('search', '')

    try:
        page = int(page)
    except ValueError:
        page = 1

    search = request.args['search'] if 'search' in request.args else ''
    query = db.session.query(Veiculo)

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(
                Veiculo.fabricante.ilike(f"%{term}%") |
                Veiculo.modelo_veiculo.ilike(f"%{term}%") |
                Veiculo.idplaca.ilike(f"%{term}%")
            )

    total = query.count()
    max_pages = math.ceil(total / 10)
    page = int(page)
    showing = 10 if page < max_pages else (total - 10 * (page - 1)) % 10
    array = query.offset((page - 1) * 10).limit(10).all()

    return render_template('veiculos/veiculos.html',
                            title='Veículos', context='veiculos',
                            array=array, total=total, page=page, search=search, max_pages=max_pages, showing=showing)

@veiculos_bp.route('/novo', methods=['GET', 'POST'])
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

    return render_template('veiculos/form_veiculo.html', titulo='Novo veículo', action=url_for('veiculos.novo_veiculo'))

@veiculos_bp.route('/edit/<string:idplaca>', methods=['GET', 'POST'])
def edit(idplaca):
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

        new_idplaca = request.form['idplaca']
        if new_idplaca != veiculo.idplaca:
            existing_veiculo = db.session.query(Veiculo).filter_by(idplaca=new_idplaca).first()
            if existing_veiculo:
                flash('Já existe um veículo com essa placa!', 'error')
                return redirect(url_for('veiculos.edit', idplaca=idplaca))
            veiculo.idplaca = new_idplaca
        db.session.add(veiculo)
        try:
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar veículo: {str(e)}', 'error')
            return redirect(url_for('veiculos.edit', idplaca=idplaca))

        db.session.commit()
        flash('Veículo atualizado com sucesso!', 'success')
        return redirect(url_for('veiculos.list_veiculos'))

    return render_template('veiculos/form_veiculo.html', titulo='Alterando veículo', action=url_for('veiculos.edit', idplaca=idplaca), veiculo=veiculo)

@veiculos_bp.route('/delete/<string:idplaca>', methods=['POST'])
def delete(idplaca):
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

@veiculos_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    data = request.get_json()
    ids_to_delete = data.get('ids', [])

    print(f"IDs: {ids_to_delete}")

    if not ids_to_delete:
        flash('Nenhum veículo selecionado para exclusão.', 'error')
        return redirect(url_for('veiculos.list_veiculos'))

    failed_deletions = []

    for idplaca in ids_to_delete:
        try:
            result = db.session.query(Veiculo).filter_by(idplaca=idplaca).first()

            if not result:
                failed_deletions.append(f'Veículo com placa {idplaca} não encontrado.')
                continue
            db.session.delete(result)

        except Exception as e:
            failed_deletions.append(f'Erro ao excluir veículo com ID {idplaca}: {str(e)}')

    try:
        db.session.commit()
    except Exception:
        flash('Erro ao realizar exclusão em massa. Tente novamente.', 'error')
        return redirect(url_for('veiculos.list_veiculos'))

    if failed_deletions:
        flash('Alguns veículos não puderam ser excluídos: ' + ', '.join(failed_deletions), 'error')
    else:
        flash('Veículos excluídos com sucesso!', 'success')

    return redirect(url_for('veiculos.list_veiculos'))
