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

cursor.execute("DELETE FROM veiculo;")
cursor.execute("DELETE FROM cliente;")
cursor.execute("DELETE FROM prestador;")
cursor.execute("DELETE FROM despesa;")


# CLIENTES
cursor.execute("INSERT INTO cliente VALUES (1, 'Abner José da Silva', 'Rua A, 123', 'Presidente Epitácio', 'SP', '01000-000');")
for i in range(2, 235):
    nome = faker.name()
    endereco = faker.address().replace('\n', ', ')
    cidade = faker.city()
    uf = faker.estado()[0].upper()
    cep = faker.postcode()

    cursor.execute(
        "INSERT INTO cliente (idcliente, nome, endereco, cidade, uf, cep) VALUES (%s, %s, %s, %s, %s, %s)",
        (i, nome, endereco, cidade, uf, cep)
    )

# PRESTADORES
for i in range(1, 38):
    nome_empresa = faker.company()
    cidade = faker.city()
    uf = faker.random_element(elements=("AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"))
    cep = faker.postcode()

    cursor.execute(
        "INSERT INTO prestador (idprestador, nome_empresa, cidade, uf, cep) VALUES (%s, %s, %s, %s, %s)",
        (i, nome_empresa, cidade, uf, cep)
    )

# VEÍCULOS
for i in range(1, 112):
    placa = faker.license_plate()
    ano = faker.year()
    modelo = ano
    fabricante = faker.random_element(elements=["Toyota", "Ford", "Chevrolet", "Honda", "Volkswagen", "Fiat", "Hyundai", "Nissan", "Jeep", "Renault"])
    modelo_veiculo = faker.random_element(elements=["Corolla", "Fiesta", "Cruze", "Civic", "Golf", "Punto", "Elantra", "Sentra", "Compass", "Duster"])
    cor = faker.color_name()[:20]  
    preco_fipe = faker.random_number(digits=6, fix_len=True) + 1000
    preco_venda = faker.random_number(digits=6, fix_len=True) + 1000
    total_despesa = faker.random_number(digits=4, fix_len=True) + 100
    
    cursor.execute(
        "INSERT INTO veiculo (idplaca, ano, modelo, preco_fipe, fabricante, modelo_veiculo, cor, preco_venda, total_despesa) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (placa, ano, modelo, preco_fipe, fabricante, modelo_veiculo, cor, preco_venda, total_despesa)
    )


conn.commit()
cursor.close()
conn.close()

