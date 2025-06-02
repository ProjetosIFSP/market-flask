from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Prestador
import math

prestadores_bp = Blueprint('prestadores', __name__, url_prefix='/prestadores')

@prestadores_bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'POST':
        page = request.form.get('page', 1)
        search = request.form.get('search', '')
    else:
      page = request.args.get('page', 1)
      search = request.args.get('search', '')

    query = db.session.query(Prestador).order_by(Prestador.nome_empresa.asc())

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Prestador.nome_empresa.ilike(f"%{term}%"))

    total = query.count()
    max_pages = math.ceil(total / 10)
    showing = 10 if int(page) < max_pages else (total - 10 * (int(page) - 1)) % 10
    array = query.offset((int(page) - 1) * 10).limit(10).all()

    return render_template('prestadores/prestadores.html',
                            title='Prestadores', context='prestadores',
                            array=array, total=total, page=page, search=search, max_pages=max_pages, showing=showing)

@prestadores_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nome_empresa = request.form['nome_empresa']
        cidade = request.form['cidade']
        uf = request.form['uf']
        cep = request.form['cep']

        idprestador = db.session.query(db.func.max(Prestador.idprestador)).scalar()
        idprestador = (idprestador + 1) if idprestador is not None else 1

        new_provider = Prestador(idprestador=idprestador, nome_empresa=nome_empresa, cidade=cidade, uf=uf, cep=cep)
        db.session.add(new_provider)
        db.session.commit()

        flash('Prestador cadastrado com sucesso!', 'success')
        return redirect(url_for('prestadores.list'))

    estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    return render_template('prestadores/form_prestador.html', estados=estados, titulo='Novo prestador', action=url_for('prestadores.add'))

@prestadores_bp.route('/edit/<int:idprestador>', methods=['GET', 'POST'])
def edit(idprestador):
    prestador = db.session.query(Prestador).filter_by(idprestador=idprestador).first()
    if not prestador:
        flash('Prestador não encontrado!', 'error')
        return redirect(url_for('prestadores.list'))

    if request.method == 'POST':
        prestador.nome_empresa = request.form['nome_empresa']
        prestador.cidade = request.form['cidade']
        prestador.uf = request.form['uf']
        prestador.cep = request.form['cep']

        db.session.commit()
        flash('Prestador atualizado com sucesso!', 'success')
        return redirect(url_for('prestadores.list'))

    estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    return render_template('prestadores/form_prestador.html', titulo='Alterando prestador', action=url_for('prestadores.edit', idprestador=idprestador), prestador=prestador, estados=estados)

@prestadores_bp.route('/delete/<int:idprestador>', methods=['POST'])
def delete(idprestador):
    prestador = db.session.query(Prestador).filter_by(idprestador=idprestador).first()

    if not prestador:
        flash('Prestador não encontrado!', 'error')
        return redirect(url_for('prestadores.list'))

    db.session.delete(prestador)
    db.session.commit()
    flash('Prestador excluído com sucesso!', 'success')
    return redirect(url_for('prestadores.list'))

@prestadores_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    print("Iniciando exclusão em massa de prestadores")

    data = request.get_json()
    ids_to_delete = data.get('ids', [])

    print(f"IDs recebidos para exclusão: {ids_to_delete}")

    if not ids_to_delete:
        flash('Nenhum prestador selecionado para exclusão.', 'error')
        return redirect(url_for('prestadores.list'))

    failed_deletions = []

    for idprestador in ids_to_delete:
        try:
            prestador = db.session.query(Prestador).filter_by(idprestador=idprestador).first()
            print(f"Excluindo prestador com ID: {idprestador}")
            if not prestador:
                failed_deletions.append(f'Prestador com ID {idprestador} não encontrado.')
                continue

            db.session.delete(prestador)
        except Exception as e:
            failed_deletions.append(f'Erro ao excluir prestador com ID {idprestador}: {str(e)}')

    try:
        db.session.commit()
    except Exception:
        flash('Erro ao realizar exclusão em massa. Tente novamente.', 'error')
        return redirect(url_for('prestadores.list'))

    if failed_deletions:
        flash('Alguns prestadores não puderam ser excluídos: ' + ', '.join(failed_deletions), 'error')
    else:
        flash('Prestadores excluídos com sucesso!', 'success')

    return redirect(url_for('prestadores.list'))
