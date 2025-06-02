from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Cliente, Venda, Compra
import math

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/', methods=['GET', 'POST'])
def list():
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
    query = db.session.query(Cliente).order_by(Cliente.nome.asc())

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Cliente.nome.ilike(f"%{term}%"))

    total = query.count()
    max_pages = math.ceil(total / 10)
    page = int(page)
    showing = 10 if page < max_pages else (total - 10 * (page - 1)) % 10
    array = query.offset((page - 1) * 10).limit(10).all()

    return render_template('clientes/clientes.html',
                            title='Clientes', context='clientes',
                            array=array, total=total, page=page, search=search, max_pages=max_pages, showing=showing)


@clientes_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        cidade = request.form['cidade']
        uf = request.form['uf']
        cep = request.form['cep']
        idcliente = db.session.query(db.func.max(Cliente.idcliente)).scalar()
        idcliente = (idcliente + 1) if idcliente is not None else 1

        new_client = Cliente(idcliente=idcliente, nome=nome, endereco=endereco, cidade=cidade, uf=uf, cep=cep)
        db.session.add(new_client)
        db.session.commit()

        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('clientes.list'))

    estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    return render_template('clientes/form_cliente.html', estados=estados, title='Novo cliente', action=url_for('clientes.add'))

@clientes_bp.route('/edit/<int:idcliente>', methods=['GET', 'POST'])
def edit(idcliente):
    cliente = db.session.query(Cliente).filter_by(idcliente=idcliente).first()
    if not cliente:
        flash('Cliente não encontrado!', 'error')
        return redirect(url_for('clientes.list'))

    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.endereco = request.form['endereco']
        cliente.cidade = request.form['cidade']
        cliente.uf = request.form['uf']
        cliente.cep = request.form['cep']

        db.session.commit()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('clientes.list'))

    estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    return render_template('clientes/form_cliente.html', title='Alterando cliente', action=url_for('clientes.edit', idcliente=idcliente), cliente=cliente, estados=estados)

@clientes_bp.route('/delete/<int:idcliente>', methods=['POST'])
def delete(idcliente):
    cliente = db.session.query(Cliente).filter_by(idcliente=idcliente).first()

    if not cliente:
        flash('Cliente não encontrado!', 'error')
        return redirect(url_for('clientes.list'))

    vendas = db.session.query(Venda).filter_by(idcliente=idcliente).count()
    compras = db.session.query(Compra).filter_by(idcliente=idcliente).count()

    if vendas > 0 or compras > 0:
        flash('Não é possível excluir o cliente, pois há vendas ou compras associadas.', 'error')
        return redirect(url_for('clientes.list'))

    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente excluído com sucesso!', 'success')
    return redirect(url_for('clientes.list'))

@clientes_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    data = request.get_json()
    ids_to_delete = data.get('ids', [])

    if not ids_to_delete:
        flash('Nenhum cliente selecionado para exclusão.', 'error')
        return redirect(url_for('clientes.list'))

    failed_deletions = []

    for idcliente in ids_to_delete:
        try:
            cliente = db.session.query(Cliente).filter_by(idcliente=idcliente).first()

            if not cliente:
                failed_deletions.append(f'Cliente com ID {idcliente} não encontrado.')
                continue

            vendas = db.session.query(Venda).filter_by(idcliente=idcliente).count()
            compras = db.session.query(Compra).filter_by(idcliente=idcliente).count()

            if vendas > 0 or compras > 0:
                failed_deletions.append(f'Cliente com ID {idcliente} possui vendas ou compras associadas.')
                continue

            db.session.delete(cliente)
        except Exception as e:
            failed_deletions.append(f'Erro ao excluir cliente com ID {idcliente}: {str(e)}')

    try:
        db.session.commit()
    except Exception:
        flash('Erro ao realizar exclusão em massa. Tente novamente.', 'error')
        return redirect(url_for('clientes.list'))

    if failed_deletions:
        flash('Alguns clientes não puderam ser excluídos: ' + ', '.join(failed_deletions), 'error')
    else:
        flash('Clientes excluídos com sucesso!', 'success')

    return redirect(url_for('clientes.list'))
