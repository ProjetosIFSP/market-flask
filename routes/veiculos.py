from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_connection import db
from models import Veiculo, Compra, Venda, Despesa, Cliente, Prestador
import math

veiculos_bp = Blueprint('veiculos', __name__, url_prefix='/veiculos')

def format_currency(currency, label, coalesce=False):
    if coalesce:
        return db.func.concat('R$ ', db.func.replace(db.func.replace(db.func.replace(db.func.to_char(db.func.coalesce(db.func.sum(db.func.distinct(currency)), 0), 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.')).label(label)
    return db.func.concat('R$ ', db.func.replace(db.func.replace(db.func.replace(db.func.to_char(currency, 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.')).label(label)

def format_date(date, label):
    return db.func.to_char(date, 'DD/MM/YYYY').label(label)

@veiculos_bp.route('/', methods=['GET', 'POST'])
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
    query = db.session.query(Veiculo)

    
    

    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(
                Veiculo.fabricante.ilike(f"%{term}%") |
                Veiculo.modelo_veiculo.ilike(f"%{term}%") |
                Veiculo.idplaca.ilike(f"%{term}%")
            )

    query = query.with_entities(
        Veiculo.idplaca,
        Veiculo.fabricante,
        Veiculo.modelo_veiculo,
        Veiculo.ano,
        Veiculo.modelo,
        Veiculo.preco_fipe,
        Veiculo.cor,
        Veiculo.preco_venda,
        Veiculo.total_despesa,
        db.func.replace(db.func.replace(db.func.replace(db.func.to_char(Veiculo.preco_fipe, 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.').label('formatted_fipe'),
        db.func.replace(db.func.replace(db.func.replace(db.func.to_char(Veiculo.preco_venda, 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.').label('formatted_venda'),
        db.func.replace(db.func.replace(db.func.replace(db.func.to_char(Veiculo.total_despesa, 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.').label('formatted_despesa'),
    )

    total = query.count()
    max_pages = math.ceil(total / 10)
    page = int(page)
    showing = 10 if page < max_pages else (total - 10 * (page - 1)) % 10
    array = query.offset((page - 1) * 10).limit(10).all()

    return render_template('veiculos/veiculos.html',
                            title='Veículos', context='veiculos',
                            array=array, total=total, page=page, search=search, max_pages=max_pages, showing=showing)

@veiculos_bp.route('/add', methods=['GET', 'POST'])
def add():
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

        new_vehicle = Veiculo(
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
        db.session.add(new_vehicle)
        db.session.commit()

        flash('Veículo cadastrado com sucesso!', 'success')
        return redirect(url_for('veiculos.list'))

    return render_template('veiculos/form_veiculo.html', title='Novo veículo', action=url_for('veiculos.add'))

@veiculos_bp.route('/edit/<string:idplaca>', methods=['GET', 'POST'])
def edit(idplaca):
    veiculo = db.session.query(Veiculo).filter_by(idplaca=idplaca).first()
    if not veiculo:
        flash('Veículo não encontrado!', 'error')
        return redirect(url_for('veiculos.list'))

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
        return redirect(url_for('veiculos.list'))

    return render_template('veiculos/form_veiculo.html', title='Alterando veículo', action=url_for('veiculos.edit', idplaca=idplaca), veiculo=veiculo)

@veiculos_bp.route('/delete/<string:idplaca>', methods=['POST'])
def delete(idplaca):
    veiculo = db.session.query(Veiculo).filter_by(idplaca=idplaca).first()

    if not veiculo:
        flash('Veículo não encontrado!', 'error')
        return redirect(url_for('veiculos.list'))

    try:
        db.session.delete(veiculo)
        db.session.commit()
        flash('Veículo excluído com sucesso!', 'success')
    except Exception:
        flash('Erro ao excluir veículo. Tente novamente.', 'error')

    return redirect(url_for('veiculos.list'))

@veiculos_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    data = request.get_json()
    ids_to_delete = data.get('ids', [])

    print(f"IDs: {ids_to_delete}")

    if not ids_to_delete:
        flash('Nenhum veículo selecionado para exclusão.', 'error')
        return redirect(url_for('veiculos.list'))

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
        return redirect(url_for('veiculos.list'))

    if failed_deletions:
        flash('Alguns veículos não puderam ser excluídos: ' + ', '.join(failed_deletions), 'error')
    else:
        flash('Veículos excluídos com sucesso!', 'success')

    return redirect(url_for('veiculos.list'))

@veiculos_bp.route('/details/<string:idplaca>', methods=['GET'])
def details(idplaca):
    veiculo = db.session.query(
        Veiculo.idplaca,
        Veiculo.fabricante,
        Veiculo.modelo_veiculo,
        Veiculo.ano,
        Veiculo.modelo,
        Veiculo.preco_fipe,
        format_currency(Veiculo.preco_fipe, 'formatted_fipe'),
        Veiculo.cor,
        Veiculo.preco_venda,
        format_currency(Veiculo.preco_venda, 'formatted_venda'),
        Veiculo.total_despesa,
        format_currency(Veiculo.total_despesa, 'formatted_despesa'),
        format_currency(Compra.valor_pago, 'total_compras', True),
        format_currency(Venda.valor_vendido, 'total_vendas', True),
        format_currency(Despesa.valor, 'total_despesas', True),
        db.func.concat('R$ ', db.func.replace(db.func.replace(db.func.replace(db.func.to_char(db.func.coalesce(db.func.sum(db.func.distinct(Venda.valor_vendido)) - db.func.sum(db.func.distinct(Compra.valor_pago)), 0), 'L999G999D99'), ',', 'TEMP'), '.', ','), 'TEMP', '.')).label('total_caixa')
    ).outerjoin(Compra, Compra.idplaca == Veiculo.idplaca) \
     .outerjoin(Venda, Venda.idplaca == Veiculo.idplaca) \
     .outerjoin(Despesa, Despesa.idplaca == Veiculo.idplaca) \
     .filter(Veiculo.idplaca == idplaca) \
     .group_by(Veiculo.idplaca).first()

    transactions = db.session.query(
        db.literal('Compra').label('tipo'),
        Compra.data.label('data'),
        format_date(Compra.data, 'formatted_data'),
        Compra.valor_pago.label('valor'),
        format_currency(Compra.valor_pago, 'formatted_valor'),
        Cliente.nome.label('cliente_nome')
    ).outerjoin(Cliente, Cliente.idcliente == Compra.idcliente)\
    .filter(Compra.idplaca == idplaca)\
    .union(
        db.session.query(
            db.literal('Venda').label('tipo'),
            Venda.data.label('data'),
            format_date(Venda.data, 'formatted_data'),
            Venda.valor_vendido.label('valor'),
            format_currency(Venda.valor_vendido, 'formatted_valor'),
            Cliente.nome.label('cliente_nome')
        ).outerjoin(Cliente, Cliente.idcliente == Venda.idcliente)\
        .filter(Venda.idplaca == idplaca)
    ).order_by(db.desc('data')).all()

    despesas = db.session.query(
        Despesa.iddespesa,
        Despesa.descricao,
        format_date(Despesa.data_servico, 'data_servico'),
        Despesa.valor,
        format_currency(Despesa.valor, 'formatted_valor'),
        Despesa.idplaca,
        Despesa.idprestador,
        Prestador.nome_empresa.label('prestador_nome')
    ).outerjoin(Prestador, Prestador.idprestador == Despesa.idprestador)

    if not veiculo:
        flash('Veículo não encontrado!', 'error')
        return redirect(url_for('veiculos.list'))

    return render_template('veiculos/details.html', title='Detalhes do Veículo', context='veiculos', \
                           veiculo=veiculo, transactions=transactions, despesas=despesas)
