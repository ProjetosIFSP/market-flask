from flask import Flask, render_template, request, jsonify
from db_connection import init_app, db
from models import Cliente
import os
import math

app = Flask(__name__)


# Inicializando o SQLAlchemy com o app Flask
init_app(app)

@app.route('/')
def index():
    return render_template('index.html', homepage=True)

@app.route('/clientes', methods=['GET'])
def list_clients():
    page = request.args['page'] if 'page' in request.args else 1
    try:
        page = int(page)
    except ValueError:
        page = 1

    search = request.args['search'] if 'search' in request.args else ''
    query = db.session.query(Cliente)


    if search:
        query = query.filter(Cliente.nome.ilike(f"%{search}%"))

    clientes = query.offset((page - 1) * 10).limit(10).all()
    total = db.session.query(Cliente).count()

    max_pages = math.ceil(total/10)

    return render_template('clientes.html', clientes=clientes, total=total, page=page, search=search, max_pages = max_pages)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

