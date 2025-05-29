CREATE TABLE IF NOT EXISTS cliente (
    idcliente INT PRIMARY KEY,
    nome VARCHAR(60),
    endereco VARCHAR(255),
    cidade VARCHAR(80),
    uf VARCHAR(2),
    cep VARCHAR(9)
);

INSERT INTO cliente VALUES (1, 'Abner J. Silva', 'Rua Número Um, 234', 'Presidente Epitácio', 'SP', '19470-000');