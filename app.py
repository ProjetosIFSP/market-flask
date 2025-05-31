from flask import Flask, render_template
from db_connection import init_app, db
from routes.clientes import clientes_bp
from routes.veiculos import veiculos_bp
from routes.prestadores import prestadores_bp

app = Flask(__name__)

# Para usar mensagens flash
app.secret_key = 'TPRC0_IFSP_2025'

init_app(app)

app.register_blueprint(clientes_bp)
app.register_blueprint(veiculos_bp)
app.register_blueprint(prestadores_bp)

@app.route('/')
def index():
    return render_template('index.html', homepage=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

