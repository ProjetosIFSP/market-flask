from faker import Faker
import psycopg2

faker = Faker(locale='pt_BR')

conn = psycopg2.connect(
    dbname="market-flask",
    user="docker",
    password="docker",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()


cursor.execute("DELETE FROM venda;")
cursor.execute("DELETE FROM compra;")
cursor.execute("DELETE FROM despesa;")
cursor.execute("DELETE FROM veiculo;")
cursor.execute("DELETE FROM cliente;")
cursor.execute("DELETE FROM prestador;")

conn.commit()
cursor.close()
conn.close()

