# Programa 5S - Sistema de Gerenciamento de Auditorias

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Sistema completo para gerenciamento de auditorias do **Programa 5S**, desenvolvido com **Flask + SQLite**. Permite avaliar itens de cada um dos 5 sensos (Seiri, Seiton, Seiso, Seiketsu, Shitsuke), vinculados a setores e responsaveis de uma empresa.

## Funcionalidades

- **Dashboard** com totais de pontos por setor e media geral ao abrir o aplicativo
- **Gerenciamento de Setores** com cadastro, edicao e exclusao
- **Gerenciamento de Responsaveis** vinculados a setores
- **Nova Auditoria** com avaliacao de 25 itens (5 por senso) de 0 a 10
- **Upload de Imagens** por item de auditoria (evidencias fotograficas)
- **Relatorios** com filtros por setor e periodo
- **Seed Script** com dados ficticios (2 auditorias por setor)
- **Docker** suporte para containerizacao

## Versoes do Visual

| Versao | Descricao | Porta |
|--------|-----------|-------|
| `5s-auditoria/` | Visual classico com sidebar escura | 5000 |
| `5s-auditoria2/` | Visual moderno com glassmorphism, gradientes, animacoes e icones SVG personalizados | 5001 |

## Estrutura do Projeto

```
Programa5S/
├── 5s-auditoria/              # Versao 1.0 (classica)
│   ├── app.py                 # Aplicacao Flask principal
│   ├── seed.py                # Script para popular dados ficticios
│   ├── requirements.txt       # Dependencias Python
│   ├── iniciar.bat            # Arquivo BAT para Windows
│   ├── Dockerfile             # Configuracao Docker
│   ├── docker-compose.yml     # Docker Compose
│   ├── templates/             # Templates HTML
│   └── static/                # CSS e uploads
│
├── 5s-auditoria2/             # Versao 2.0 (moderna)
│   ├── app.py                 # Aplicacao Flask principal
│   ├── seed.py                # Script para popular dados ficticios
│   ├── requirements.txt       # Dependencias Python
│   ├── iniciar.bat            # Arquivo BAT para Windows
│   ├── Dockerfile             # Configuracao Docker
│   ├── docker-compose.yml     # Docker Compose
│   ├── templates/             # Templates HTML modernos
│   └── static/                # CSS moderno e uploads
│
└── .gitignore
```

## Estrutura do Banco de Dados

```
setores (id, nome, descricao)
    ↓
responsaveis (id, nome, email, setor_id FK)
    ↓
auditorias (id, setor_id FK, responsavel_id FK, auditor, data_auditoria, observacoes)
    ↓
itens_auditoria (id, auditoria_id FK, senso, item, nota 0-10, imagem)
```

## API

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/responsaveis_por_setor/<id>` | GET | Retorna responsaveis de um setor (JSON) |

## Como Executar

### Opcao 1: Executar direto (Python)

```bash
# Navegue para a versao desejada
cd 5s-auditoria      # ou 5s-auditoria2

# Instale as dependencias
pip install -r requirements.txt

# Execute o seed para popular dados ficticios (opcional)
python seed.py

# Inicie o servidor
python app.py
```

Acesse: http://127.0.0.1:5000 (v1) ou http://127.0.0.1:5001 (v2)

### Opcao 2: Windows (BAT)

```bash
# Execute o arquivo BAT
iniciar.bat
```

### Opcao 3: Docker

```bash
# Navegue para a versao desejada
cd 5s-auditoria      # ou 5s-auditoria2

# Execute com Docker Compose
docker-compose up --build
```

## Os 5 Sensos

| Senso | Icone | Descricao |
|-------|-------|-----------|
| **Seiri** (Utilizacao) | 🔍 | Separar o necessario do desnecessario |
| **Seiton** (Organizacao) | 📦 | Organizar e ter tudo no lugar |
| **Seiso** (Limpeza) | ✨ | Manter o local limpo |
| **Seiketsu** (Padronizacao) | 📋 | Padronizar processos |
| **Shitsuke** (Disciplina) | 🎯 | Manter os habitos |

## Tecnologias

- **Backend:** Python 3.12, Flask 3.x
- **Banco de Dados:** SQLite3
- **Frontend:** HTML5, CSS3 (glassmorphism, gradientes, animacoes), JavaScript vanilla
- **Icones:** SVG inline personalizados (estilo Lucide)
- **Container:** Docker, Docker Compose
- **Fonte:** Plus Jakarta Sans (Google Fonts)

## Contribuindo

Contribuicoes sao bem-vindas! Fork o repositorio, crie uma branch para sua feature e abra um Pull Request.

## Licenca

Este projeto esta sob a licenca MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

Feito com dedication por [VAW1970](https://github.com/VAW1970)
