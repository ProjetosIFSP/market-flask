CREATE TABLE IF NOT EXISTS cliente (
    idcliente INT PRIMARY KEY,
    nome VARCHAR(60),
    endereco VARCHAR(255),
    cidade VARCHAR(80),
    uf VARCHAR(2),
    cep VARCHAR(9)
);

CREATE TABLE IF NOT EXISTS veiculo (
    idplaca VARCHAR(9) PRIMARY KEY,
    ano INT,
    modelo INT,
    preco_fipe DECIMAL(10,2),
    fabricante VARCHAR(50),
    modelo_veiculo VARCHAR(60),
    cor VARCHAR(20),
    preco_venda DECIMAL(10,2),
    total_despesa DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS venda (
    idvenda INT PRIMARY KEY,
    data DATE,
    valor_vendido DECIMAL(10,2),
    idcliente INT,
    idplaca VARCHAR(9),
    forma_pagamento VARCHAR(40),
    FOREIGN KEY (idcliente) REFERENCES cliente(idcliente),
    FOREIGN KEY (idplaca) REFERENCES veiculo(idplaca)
);

CREATE TABLE IF NOT EXISTS compra (
    idcompra INT PRIMARY KEY,
    idplaca VARCHAR(9),
    idcliente INT,
    data DATE,
    valor_pago DECIMAL(10,2),
    forma_pagamento VARCHAR(40),
    FOREIGN KEY (idplaca) REFERENCES veiculo(idplaca),
    FOREIGN KEY (idcliente) REFERENCES cliente(idcliente)
);

CREATE TABLE IF NOT EXISTS prestador (
    idprestador INT PRIMARY KEY,
    nome_empresa VARCHAR(60),
    cidade VARCHAR(80),
    uf VARCHAR(2),
    cep VARCHAR(9)
);

CREATE TABLE IF NOT EXISTS despesa (
    iddespesa INT PRIMARY KEY,
    idplaca VARCHAR(9),
    descricao VARCHAR(80),
    valor DECIMAL(10,2),
    idprestador INT,
    data_servico DATE,
    FOREIGN KEY (idplaca) REFERENCES veiculo(idplaca),
    FOREIGN KEY (idprestador) REFERENCES prestador(idprestador)
);