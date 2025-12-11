import sqlite3

DB = "detran.db"

def conectar():
    conn = sqlite3.connect(DB)
    # ATENÇÃO: Linha adicionada para o SQLite respeitar as relações entre tabelas
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS condutores (
            cpf TEXT PRIMARY KEY,
            nome TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            placa TEXT PRIMARY KEY,
            modelo TEXT,
            valor REAL,
            cpf TEXT,
            ano INTEGER,
            FOREIGN KEY(cpf) REFERENCES condutores(cpf)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS multas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano INTEGER,
            descricao TEXT,
            pontos INTEGER,
            placa TEXT,
            cpf TEXT,
            FOREIGN KEY(placa) REFERENCES veiculos(placa),
            FOREIGN KEY(cpf) REFERENCES condutores(cpf)
        )
    """)

    conn.commit()
    conn.close()

# ----------------- CONDUTORES -----------------

def salvar_condutor(cpf, nome):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO condutores VALUES (?,?)", (cpf, nome))
        conn.commit()
        return {"cpf": cpf, "nome": nome}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

# ----------------- VEÍCULOS -----------------

def emplacar(placa, modelo, valor, cpf, ano):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO veiculos VALUES (?,?,?,?,?)",
                  (placa, modelo, valor, cpf, ano))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def transferir(placa, novo_cpf):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("UPDATE veiculos SET cpf=? WHERE placa=?", (novo_cpf, placa))
        conn.commit()
        # Verifica se alguma linha foi alterada (se a placa existia)
        ok = c.rowcount > 0
        return ok
    except sqlite3.IntegrityError:
        # Falha se o novo_cpf não existir na tabela condutores
        return False
    finally:
        conn.close()

def calcular_ipva(placa):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT valor FROM veiculos WHERE placa=?", (placa,))
    row = c.fetchone()
    conn.close()
    if row:
        return round(row[0] * 0.02, 2)
    return None

# ----------------- MULTAS -----------------

def salvar_multa(ano, descricao, pontos, placa):
    conn = conectar()
    c = conn.cursor()

    # 1. Descobrir quem é o dono atual do veículo
    c.execute("SELECT cpf FROM veiculos WHERE placa=?", (placa,))
    dono = c.fetchone()
    
    if not dono:
        conn.close()
        return False # Carro não existe

    cpf_dono = dono[0]

    try:
        c.execute("""
            INSERT INTO multas (ano, descricao, pontos, placa, cpf)
            VALUES (?,?,?,?,?)
        """, (ano, descricao, pontos, placa, cpf_dono))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()