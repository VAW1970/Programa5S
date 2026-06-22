#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de popular dados fictícios para o Programa 5S
Gera pelo menos 2 auditorias por setor com notas realistas
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta

# Importar itens dos sensos do app principal (evita duplicação)
from app import SENSOS_ITEMS, init_db

# ─── Dados fictícios ────────────────────────────────────────────────────────
RESPONSAVEIS_POR_SETOR = {
    "Produção": [
        ("Carlos Silva", "carlos.silva@empresa.com"),
        ("Maria Santos", "maria.santos@empresa.com"),
    ],
    "Administrativo": [
        ("Ana Oliveira", "ana.oliveira@empresa.com"),
        ("Pedro Costa", "pedro.costa@empresa.com"),
    ],
    "Estoque": [
        ("João Pereira", "joao.pereira@empresa.com"),
        ("Lucia Ferreira", "lucia.ferreira@empresa.com"),
    ],
    "Qualidade": [
        ("Roberto Almeida", "roberto.almeida@empresa.com"),
        ("Fernanda Lima", "fernanda.lima@empresa.com"),
    ],
    "Manutenção": [
        ("Marcos Souza", "marcos.souza@empresa.com"),
        ("Juliana Rocha", "juliana.rocha@empresa.com"),
    ],
    "RH": [
        ("Patricia Mendes", "patricia.mendes@empresa.com"),
        ("Ricardo Gomes", "ricardo.gomes@empresa.com"),
    ],
}

AUDITORES = [
    "Eng. Paulo Ribeiro",
    "Dra. Camila Dias",
    "Eng. Fernando Barbosa",
    "Dra. Tatiana Nunes",
]

OBSERVACOES_ALEATORIAS = [
    "Auditoria realizada no período da manhã. Equipe demonstrou comprometimento.",
    "Observou-se melhoria significativa em relação à auditoria anterior.",
    "Necessário reforçar treinamento sobre descarte de resíduos.",
    "Setor apresentou excelente organização. Parabéns à equipe!",
    "Identificadas oportunidades de melhoria nos procedimentos de limpeza.",
    "Auditoria noturna. Alguns pontos precisam de atenção urgente.",
    "Primeira auditoria do setor. Estabelecer linha de base para comparativos.",
    "Documentação dos procedimentos precisa ser atualizada.",
    "Áreas de difícil acesso apresentaram acúmulo de resíduos.",
    "Liderança do setor demonstrou forte comprometimento com o programa.",
    "Notas gerais do auditor: setor está em constante evolução.",
    "Recomendado monitoramento mensal para manter os padrões alcançados.",
]


def gerar_nota(perfil="equilibrado"):
    """Gera uma nota realista baseada no perfil do setor"""
    if perfil == "excelente":
        return random.choices(range(7, 11), weights=[1, 2, 3, 2])[0]
    elif perfil == "regular":
        return random.choices(range(4, 8), weights=[1, 2, 2, 1])[0]
    elif perfil == "critico":
        return random.choices(range(1, 6), weights=[1, 2, 2, 1, 1])[0]
    else:  # equilibrado
        return random.choices(range(3, 10), weights=[1, 1, 2, 3, 2, 2, 1])[0]


def seed_database():
    # Garantir que as tabelas existam
    init_db()

    # Conectar ao banco e inicializar tabelas
    db = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auditoria_5s.db'))
    db.execute("PRAGMA foreign_keys = ON")

    # Verificar se já existem dados
    cursor = db.execute("SELECT COUNT(*) FROM auditorias")
    if cursor.fetchone()[0] > 0:
        print("[!] Ja existem auditorias no banco. Limpando dados existentes...")
        db.execute("DELETE FROM itens_auditoria")
        db.execute("DELETE FROM auditorias")
        db.execute("DELETE FROM responsaveis")
        db.commit()

    print("[5S] Populando banco de dados ficticio...")
    print()

    # ─── 1. Inserir responsáveis ─────────────────────────────────────────
    print("[+] Cadastrando responsaveis...")
    responsaveis_map = {}  # {setor_nome: [(id, nome), ...]}

    for setor_nome, resp_list in RESPONSAVEIS_POR_SETOR.items():
        # Buscar ID do setor
        cursor = db.execute("SELECT id FROM setores WHERE nome = ?", (setor_nome,))
        setor_row = cursor.fetchone()
        if not setor_row:
            print(f"  [!] Setor '{setor_nome}' nao encontrado, pulando...")
            continue

        setor_id = setor_row[0]
        responsaveis_map[setor_nome] = []

        for nome, email in resp_list:
            cursor = db.execute(
                "INSERT INTO responsaveis (nome, email, setor_id) VALUES (?, ?, ?)",
                (nome, email, setor_id)
            )
            resp_id = cursor.lastrowid
            responsaveis_map[setor_nome].append((resp_id, setor_id, nome))
            print(f"  [OK] {nome} -> {setor_nome}")

    db.commit()

    # ─── 2. Criar auditorias (2 por setor) ──────────────────────────────
    print()
    print("[+] Criando auditorias...")

    # Perfis de desempenho por setor para variar os dados
    perfis_setores = {
        "Produção": ["excelente", "regular"],
        "Administrativo": ["equilibrado", "regular"],
        "Estoque": ["critico", "regular"],
        "Qualidade": ["excelente", "excelente"],
        "Manutenção": ["regular", "critico"],
        "RH": ["equilibrado", "excelente"],
    }

    # Datas base para as auditorias
    data_base = datetime(2026, 6, 1)

    total_auditorias = 0
    total_itens = 0

    for setor_nome, resp_list in responsaveis_map.items():
        perfis = perfis_setores.get(setor_nome, ["equilibrado", "equilibrado"])

        for i, (resp_id, setor_id, resp_nome) in enumerate(resp_list):
            perfil = perfis[i % len(perfis)]

            # Gerar data aleatória nos últimos 60 dias
            dias_aleatorios = random.randint(0, 60)
            data_auditoria = (data_base + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")

            auditor = random.choice(AUDITORES)
            observacoes = random.choice(OBSERVACOES_ALEATORIAS)

            # Inserir auditoria
            cursor = db.execute(
                "INSERT INTO auditorias (setor_id, responsavel_id, auditor, data_auditoria, observacoes) "
                "VALUES (?, ?, ?, ?, ?)",
                (setor_id, resp_id, auditor, data_auditoria, observacoes)
            )
            auditoria_id = cursor.lastrowid

            # Gerar notas para cada senso
            notas_por_senso = {}
            for senso, items in SENSOS_ITEMS.items():
                for idx, item in enumerate(items):
                    nota = gerar_nota(perfil)
                    db.execute(
                        "INSERT INTO itens_auditoria (auditoria_id, senso, item, nota) "
                        "VALUES (?, ?, ?, ?)",
                        (auditoria_id, senso, item, nota)
                    )
                    total_itens += 1

                    if senso not in notas_por_senso:
                        notas_por_senso[senso] = []
                    notas_por_senso[senso].append(nota)

            # Calcular média da auditoria
            todas_notas = [n for notas in notas_por_senso.values() for n in notas]
            media = sum(todas_notas) / len(todas_notas) if todas_notas else 0

            print(f"  [AUD] Auditoria #{auditoria_id} - {setor_nome} ({resp_nome})")
            print(f"         Data: {data_auditoria} | Auditor: {auditor} | Media: {media:.1f}")
            for senso, notas in notas_por_senso.items():
                media_senso = sum(notas) / len(notas)
                print(f"       {senso}: {media_senso:.1f}")

            total_auditorias += 1

    db.commit()
    db.close()

    print()
    print("=" * 60)
    print(f"  [OK] Seed concluido com sucesso!")
    print(f"  [RES] {total_auditorias} auditorias criadas")
    print(f"  [RES] {total_itens} itens avaliados")
    print(f"  [RES] {len(responsaveis_map)} setores com dados")
    print("=" * 60)


if __name__ == '__main__':
    seed_database()
