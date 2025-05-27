from flask import Flask, render_template, request, jsonify
from db_connection import init_app, db
from models import Cliente
import os

app = Flask(__name__)

# Inicializando o SQLAlchemy com o app Flask
init_app(app)

@app.route('/')
def index():
    return render_template('index.html', homepage=True)

@app.route('/clientes', methods=['GET'])
def list_clients():
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '')
    query = db.session.query(Cliente)

    if search:
        query = query.filter(Cliente.nome.ilike(f"%{search}%"))

    clientes = query.offset((page - 1) * 10).limit(10).all()
    total = query.count()

    return render_template('clientes.html', clientes=clientes, total=total, page=page, search=search)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

