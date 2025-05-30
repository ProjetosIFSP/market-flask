from faker import Faker
import psycopg2

# Configuração do Faker
faker = Faker()

# Conexão com o banco de dados
conn = psycopg2.connect(
    dbname="market-flask",
    user="docker",
    password="docker",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Gerar e inserir 234 clientes
for i in range(1, 235):
    nome = faker.name()
    endereco = faker.address().replace('\n', ', ')
    cidade = faker.city()
    uf = faker.random_element(elements=("AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"))
    cep = faker.zipcode()

    cursor.execute(
        "INSERT INTO cliente (idcliente, nome, endereco, cidade, uf, cep) VALUES (%s, %s, %s, %s, %s, %s)",
        (i, nome, endereco, cidade, uf, cep)
    )

# Commit e fechamento
conn.commit()
cursor.close()
conn.close()

print("234 clientes inseridos com sucesso!")
