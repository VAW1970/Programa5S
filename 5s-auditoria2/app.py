#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa 5S - Sistema de Gerenciamento de Auditorias
Flask + SQLite
"""

import os
import uuid
import sqlite3
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, g, send_file, send_from_directory
)

app = Flask(__name__)
app.secret_key = '5s-auditoria-secret-key-2026'

DATABASE = os.environ.get('DATABASE', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auditoria_5s.db'))

# Configuracao de upload de imagens
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    """Salva arquivo upload com nome unico e retorna o nome do arquivo"""
    if file and file.filename and allowed_file(file.filename):
        # Verificar tamanho do arquivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > MAX_FILE_SIZE:
            return None
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex[:12]}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return filename
    return None

# ─── Itens padrão dos 5S ───────────────────────────────────────────────────
SENSOS_ITEMS = {
    "Seiri (Utilização)": [
        "Itens desnecessários foram removidos do local?",
        "Materiais obsoletos foram descartados?",
        "Há excesso de ferramentas ou equipamentos?",
        "Os itens necessários estão acessíveis?",
        "O volume de itens é adequado ao espaço disponível?",
    ],
    "Seiton (Organização)": [
        "Os itens estão organizados por frequência de uso?",
        "Há locais definidos para cada item?",
        "As áreas de trabalho estão limpas e livres?",
        "Os materiais estão sinalizados e identificados?",
        "O fluxo de trabalho é lógico e eficiente?",
    ],
    "Seiso (Limpeza)": [
        "O local está limpo e livre de sujeira?",
        "Os equipamentos estão limpos e conservados?",
        "Há rotina de limpeza definida?",
        "Os resíduos são descartados adequadamente?",
        "As áreas de difícil acesso estão limpas?",
    ],
    "Seiketsu (Padronização)": [
        "Há procedimentos padrão documentados?",
        "Os padrões de limpeza são cumpridos?",
        "Os locais de armazenamento são padronizados?",
        "Há indicadores visuais de organização?",
        "As equipes conhecem os padrões estabelecidos?",
    ],
    "Shitsuke (Disciplina)": [
        "Os colaboradores seguem os procedimentos?",
        "Há hábitos de autocontrole?",
        "As auditorias internas são realizadas?",
        "Há registro de melhorias implementadas?",
        "A liderança dá o exemplo?",
    ],
}

SENSES_INFO = {
    "Seiri (Utilização)": {
        "icon": '<svg viewBox="0 0 40 40" width="32" height="32"><circle cx="20" cy="14" r="7" fill="currentColor" fill-opacity=".15" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M12 32c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M26 12l4-4m-2 2l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="32" cy="10" r="4" fill="currentColor" opacity=".1"/></svg>',
        "color": "#e74c3c",
        "desc": "Separar o necessário do desnecessário"
    },
    "Seiton (Organização)": {
        "icon": '<svg viewBox="0 0 40 40" width="32" height="32"><circle cx="20" cy="14" r="7" fill="currentColor" fill-opacity=".15" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M12 32c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><rect x="15" y="6" width="10" height="3" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M17 7.5h6" stroke="currentColor" stroke-width="1" stroke-linecap="round"/></svg>',
        "color": "#f39c12",
        "desc": "Organizar e ter tudo no lugar"
    },
    "Seiso (Limpeza)": {
        "icon": '<svg viewBox="0 0 40 40" width="32" height="32"><circle cx="20" cy="14" r="7" fill="currentColor" fill-opacity=".15" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M12 32c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M24 8l3-3m0 0l-3-3m3 3l3 3m-3-3l-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity=".7"/><path d="M12 8l2-2m0 0l-2-2m2 2l2 2m-2-2l-2 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity=".5"/></svg>',
        "color": "#27ae60",
        "desc": "Manter o local limpo"
    },
    "Seiketsu (Padronização)": {
        "icon": '<svg viewBox="0 0 40 40" width="32" height="32"><circle cx="20" cy="14" r="7" fill="currentColor" fill-opacity=".15" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M12 32c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><rect x="14" y="5" width="12" height="8" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M16 8h8M16 10.5h5" stroke="currentColor" stroke-width="1" stroke-linecap="round"/></svg>',
        "color": "#3498db",
        "desc": "Padronizar processos"
    },
    "Shitsuke (Disciplina)": {
        "icon": '<svg viewBox="0 0 40 40" width="32" height="32"><circle cx="20" cy="14" r="7" fill="currentColor" fill-opacity=".15" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M12 32c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5"/><path d="M17 6l3 3 6-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        "color": "#9b59b6",
        "desc": "Manter os hábitos"
    },
}


# ─── Database helpers ──────────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS setores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS responsaveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT DEFAULT '',
            setor_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (setor_id) REFERENCES setores(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS auditorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setor_id INTEGER NOT NULL,
            responsavel_id INTEGER NOT NULL,
            auditor TEXT NOT NULL DEFAULT '',
            data_auditoria DATE NOT NULL,
            observacoes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (setor_id) REFERENCES setores(id),
            FOREIGN KEY (responsavel_id) REFERENCES responsaveis(id)
        );

        CREATE TABLE IF NOT EXISTS itens_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auditoria_id INTEGER NOT NULL,
            senso TEXT NOT NULL,
            item TEXT NOT NULL,
            nota INTEGER NOT NULL CHECK(nota >= 0 AND nota <= 10),
            imagem TEXT DEFAULT '',
            FOREIGN KEY (auditoria_id) REFERENCES auditorias(id) ON DELETE CASCADE
        );
    """)

    # Migracao: adicionar coluna imagem se nao existir (bancos antigos)
    try:
        db.execute("ALTER TABLE itens_auditoria ADD COLUMN imagem TEXT DEFAULT ''")
        db.commit()
    except sqlite3.OperationalError:
        pass  # Coluna ja existe

    # Inserir setores padrão se a tabela estiver vazia
    cursor = db.execute("SELECT COUNT(*) FROM setores")
    if cursor.fetchone()[0] == 0:
        setores_padrao = [
            ("Produção", "Setor de produção industrial"),
            ("Administrativo", "Departamento administrativo"),
            ("Estoque", "Setor de armazenamento e depósito"),
            ("Qualidade", "Controle de qualidade"),
            ("Manutenção", "Setor de manutenção industrial"),
            ("RH", "Recursos Humanos"),
        ]
        db.executemany("INSERT INTO setores (nome, descricao) VALUES (?, ?)", setores_padrao)
        db.commit()

    db.close()


# ─── Context processors ────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    return {
        'SENSOS_ITEMS': SENSOS_ITEMS,
        'SENSES_INFO': SENSES_INFO,
        'now': datetime.now(),
    }


# ─── Dashboard ─────────────────────────────────────────────────────────────
@app.route('/')
def dashboard():
    db = get_db()

    # Totais por setor
    setores = db.execute("""
        SELECT s.id, s.nome, s.descricao,
               COUNT(DISTINCT a.id) AS total_auditorias,
               COALESCE(ROUND(AVG(ia.nota), 1), 0) AS media_geral,
               COALESCE(SUM(ia.nota), 0) AS soma_pontos
        FROM setores s
        LEFT JOIN auditorias a ON a.setor_id = s.id
        LEFT JOIN itens_auditoria ia ON ia.auditoria_id = a.id
        GROUP BY s.id
        ORDER BY s.nome
    """).fetchall()

    # Totais por senso (geral)
    totais_sensos = db.execute("""
        SELECT senso, ROUND(AVG(nota), 1) AS media, COUNT(*) AS total_itens
        FROM itens_auditoria
        GROUP BY senso
    """).fetchall()

    # Últimas auditorias
    ultimas = db.execute("""
        SELECT a.id, a.data_auditoria, a.auditor,
               s.nome AS setor_nome,
               r.nome AS responsavel_nome,
               ROUND(AVG(ia.nota), 1) AS media
        FROM auditorias a
        JOIN setores s ON s.id = a.setor_id
        JOIN responsaveis r ON r.id = a.responsavel_id
        LEFT JOIN itens_auditoria ia ON ia.auditoria_id = a.id
        GROUP BY a.id
        ORDER BY a.created_at DESC
        LIMIT 5
    """).fetchall()

    # Estatísticas gerais
    stats = db.execute("""
        SELECT
            (SELECT COUNT(*) FROM auditorias) AS total_auditorias,
            (SELECT COUNT(*) FROM setores) AS total_setores,
            (SELECT COUNT(*) FROM responsaveis) AS total_responsaveis,
            (SELECT ROUND(AVG(nota), 1) FROM itens_auditoria) AS media_geral
    """).fetchone()

    return render_template('dashboard.html',
                           setores=setores,
                           totais_sensos=totais_sensos,
                           ultimas=ultimas,
                           stats=stats)


# ─── Setores ───────────────────────────────────────────────────────────────
@app.route('/setores')
def listar_setores():
    db = get_db()
    setores = db.execute("""
        SELECT s.*, COUNT(r.id) AS total_responsaveis
        FROM setores s
        LEFT JOIN responsaveis r ON r.setor_id = s.id
        GROUP BY s.id
        ORDER BY s.nome
    """).fetchall()
    return render_template('setores.html', setores=setores)


@app.route('/setores/novo', methods=['POST'])
def novo_setor():
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if not nome:
        flash('Nome do setor é obrigatório!', 'error')
        return redirect(url_for('listar_setores'))

    db = get_db()
    try:
        db.execute("INSERT INTO setores (nome, descricao) VALUES (?, ?)", (nome, descricao))
        db.commit()
        flash(f'Setor "{nome}" criado com sucesso!', 'success')
    except sqlite3.IntegrityError:
        flash('Já existe um setor com esse nome!', 'error')

    return redirect(url_for('listar_setores'))


@app.route('/setores/<int:id>/editar', methods=['POST'])
def editar_setor(id):
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if not nome:
        flash('Nome do setor é obrigatório!', 'error')
        return redirect(url_for('listar_setores'))

    db = get_db()
    try:
        db.execute("UPDATE setores SET nome=?, descricao=? WHERE id=?", (nome, descricao, id))
        db.commit()
        flash('Setor atualizado com sucesso!', 'success')
    except sqlite3.IntegrityError:
        flash('Já existe um setor com esse nome!', 'error')

    return redirect(url_for('listar_setores'))


@app.route('/setores/<int:id>/excluir', methods=['POST'])
def excluir_setor(id):
    db = get_db()
    db.execute("DELETE FROM setores WHERE id=?", (id,))
    db.commit()
    flash('Setor excluído com sucesso!', 'success')
    return redirect(url_for('listar_setores'))


# ─── Responsáveis ──────────────────────────────────────────────────────────
@app.route('/responsaveis')
def listar_responsaveis():
    db = get_db()
    responsaveis = db.execute("""
        SELECT r.*, s.nome AS setor_nome
        FROM responsaveis r
        JOIN setores s ON s.id = r.setor_id
        ORDER BY s.nome, r.nome
    """).fetchall()
    setores = db.execute("SELECT * FROM setores ORDER BY nome").fetchall()
    return render_template('responsaveis.html', responsaveis=responsaveis, setores=setores)


@app.route('/responsaveis/novo', methods=['POST'])
def novo_responsavel():
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip()
    setor_id = request.form.get('setor_id', type=int)

    if not nome or not setor_id:
        flash('Nome e setor são obrigatórios!', 'error')
        return redirect(url_for('listar_responsaveis'))

    db = get_db()
    db.execute("INSERT INTO responsaveis (nome, email, setor_id) VALUES (?, ?, ?)",
               (nome, email, setor_id))
    db.commit()
    flash(f'Responsável "{nome}" cadastrado com sucesso!', 'success')
    return redirect(url_for('listar_responsaveis'))


@app.route('/responsaveis/<int:id>/excluir', methods=['POST'])
def excluir_responsavel(id):
    db = get_db()
    db.execute("DELETE FROM responsaveis WHERE id=?", (id,))
    db.commit()
    flash('Responsável excluído com sucesso!', 'success')
    return redirect(url_for('listar_responsaveis'))


# ─── Auditorias ────────────────────────────────────────────────────────────
@app.route('/auditorias')
def listar_auditorias():
    db = get_db()
    auditorias = db.execute("""
        SELECT a.*, s.nome AS setor_nome, r.nome AS responsavel_nome,
               ROUND(AVG(ia.nota), 1) AS media,
               COUNT(ia.id) AS total_itens
        FROM auditorias a
        JOIN setores s ON s.id = a.setor_id
        JOIN responsaveis r ON r.id = a.responsavel_id
        LEFT JOIN itens_auditoria ia ON ia.auditoria_id = a.id
        GROUP BY a.id
        ORDER BY a.created_at DESC
    """).fetchall()
    return render_template('auditorias.html', auditorias=auditorias)


@app.route('/auditoria/nova')
def nova_auditoria():
    db = get_db()
    setores = db.execute("SELECT * FROM setores ORDER BY nome").fetchall()
    responsaveis = db.execute("""
        SELECT r.*, s.nome AS setor_nome
        FROM responsaveis r
        JOIN setores s ON s.id = r.setor_id
        ORDER BY s.nome, r.nome
    """).fetchall()
    return render_template('auditoria.html', setores=setores, responsaveis=responsaveis, auditoria=None)


@app.route('/auditoria/salvar', methods=['POST'])
def salvar_auditoria():
    setor_id = request.form.get('setor_id', type=int)
    responsavel_id = request.form.get('responsavel_id', type=int)
    auditor = request.form.get('auditor', '').strip()
    data_auditoria = request.form.get('data_auditoria', '')
    observacoes = request.form.get('observacoes', '').strip()

    if not setor_id or not responsavel_id or not auditor or not data_auditoria:
        flash('Preencha todos os campos obrigatórios!', 'error')
        return redirect(url_for('nova_auditoria'))

    db = get_db()
    cursor = db.execute(
        "INSERT INTO auditorias (setor_id, responsavel_id, auditor, data_auditoria, observacoes) VALUES (?, ?, ?, ?, ?)",
        (setor_id, responsavel_id, auditor, data_auditoria, observacoes)
    )
    auditoria_id = cursor.lastrowid

    # Salvar notas dos itens
    for senso, items in SENSOS_ITEMS.items():
        for idx, item in enumerate(items):
            nota = request.form.get(f'nota_{senso}_{idx}', type=int)
            if nota is not None:
                # Processar upload de imagem
                imagem_nome = ''
                imagem_file = request.files.get(f'imagem_{senso}_{idx}')
                if imagem_file and imagem_file.filename:
                    imagem_nome = save_upload(imagem_file) or ''

                db.execute(
                    "INSERT INTO itens_auditoria (auditoria_id, senso, item, nota, imagem) VALUES (?, ?, ?, ?, ?)",
                    (auditoria_id, senso, item, nota, imagem_nome)
                )

    db.commit()
    flash('Auditoria salva com sucesso!', 'success')
    return redirect(url_for('ver_auditoria', id=auditoria_id))


@app.route('/auditoria/<int:id>')
def ver_auditoria(id):
    db = get_db()
    auditoria = db.execute("""
        SELECT a.*, s.nome AS setor_nome, r.nome AS responsavel_nome, r.email AS responsavel_email
        FROM auditorias a
        JOIN setores s ON s.id = a.setor_id
        JOIN responsaveis r ON r.id = a.responsavel_id
        WHERE a.id = ?
    """, (id,)).fetchone()

    if not auditoria:
        flash('Auditoria não encontrada!', 'error')
        return redirect(url_for('listar_auditorias'))

    itens = db.execute(
        "SELECT * FROM itens_auditoria WHERE auditoria_id = ? ORDER BY senso, id", (id,)
    ).fetchall()

    # Agrupar itens por senso
    itens_por_senso = {}
    for item in itens:
        senso = item['senso']
        if senso not in itens_por_senso:
            itens_por_senso[senso] = []
        itens_por_senso[senso].append(item)

    # Calcular médias por senso
    medias_sensos = {}
    for senso, items in itens_por_senso.items():
        notas = [item['nota'] for item in items]
        medias_sensos[senso] = round(sum(notas) / len(notas), 1) if notas else 0

    return render_template('ver_auditoria.html',
                           auditoria=auditoria,
                           itens_por_senso=itens_por_senso,
                           medias_sensos=medias_sensos)


@app.route('/auditoria/<int:id>/excluir', methods=['POST'])
def excluir_auditoria(id):
    db = get_db()
    db.execute("DELETE FROM auditorias WHERE id=?", (id,))
    db.commit()
    flash('Auditoria excluída com sucesso!', 'success')
    return redirect(url_for('listar_auditorias'))


# ─── Relatórios ────────────────────────────────────────────────────────────
@app.route('/relatorio')
def relatorio():
    db = get_db()

    setor_id = request.args.get('setor_id', type=int)
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

    query = """
        SELECT a.id, a.data_auditoria, a.auditor, a.observacoes,
               s.nome AS setor_nome,
               r.nome AS responsavel_nome
        FROM auditorias a
        JOIN setores s ON s.id = a.setor_id
        JOIN responsaveis r ON r.id = a.responsavel_id
        WHERE 1=1
    """
    params = []

    if setor_id:
        query += " AND a.setor_id = ?"
        params.append(setor_id)
    if data_inicio:
        query += " AND a.data_auditoria >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND a.data_auditoria <= ?"
        params.append(data_fim)

    query += " ORDER BY a.data_auditoria DESC, s.nome"

    auditorias = db.execute(query, params).fetchall()

    # Dados de cada auditoria
    dados_auditorias = []
    for aud in auditorias:
        itens = db.execute(
            "SELECT senso, nota FROM itens_auditoria WHERE auditoria_id = ?", (aud['id'],)
        ).fetchall()

        medias_sensos = {}
        totais_sensos = {}
        for item in itens:
            senso = item['senso']
            if senso not in totais_sensos:
                totais_sensos[senso] = {'soma': 0, 'count': 0}
            totais_sensos[senso]['soma'] += item['nota']
            totais_sensos[senso]['count'] += 1

        for senso, dados in totais_sensos.items():
            medias_sensos[senso] = round(dados['soma'] / dados['count'], 1) if dados['count'] > 0 else 0

        total_pontos = sum(d['soma'] for d in totais_sensos.values())
        total_itens = sum(d['count'] for d in totais_sensos.values())
        media_geral = round(total_pontos / total_itens, 1) if total_itens > 0 else 0

        dados_auditorias.append({
            'auditoria': aud,
            'medias_sensos': medias_sensos,
            'media_geral': media_geral,
            'total_pontos': total_pontos,
        })

    # Resumo por setor
    resumo_setores = db.execute("""
        SELECT s.nome,
               COUNT(DISTINCT a.id) AS total_auditorias,
               ROUND(AVG(ia.nota), 1) AS media_geral,
               SUM(ia.nota) AS soma_pontos
        FROM setores s
        LEFT JOIN auditorias a ON a.setor_id = s.id
        LEFT JOIN itens_auditoria ia ON ia.auditoria_id = a.id
        WHERE a.id IS NOT NULL
        GROUP BY s.id
        ORDER BY media_geral DESC
    """).fetchall()

    setores = db.execute("SELECT * FROM setores ORDER BY nome").fetchall()

    return render_template('relatorio.html',
                           dados_auditorias=dados_auditorias,
                           resumo_setores=resumo_setores,
                           setores=setores,
                           setor_id_filtro=setor_id,
                           data_inicio=data_inicio,
                           data_fim=data_fim)


# ─── API para AJAX ─────────────────────────────────────────────────────────
@app.route('/api/responsaveis_por_setor/<int:setor_id>')
def responsaveis_por_setor(setor_id):
    db = get_db()
    responsaveis = db.execute(
        "SELECT id, nome FROM responsaveis WHERE setor_id = ? ORDER BY nome", (setor_id,)
    ).fetchall()
    return jsonify([dict(r) for r in responsaveis])


# ─── Init & Run ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("\n" + "=" * 60)
    print("  🏢 Programa 5S – Sistema de Gerenciamento de Auditorias")
    print("  📊 Acesse: http://127.0.0.1:5001")
    print("=" * 60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5001)
