# Flask Supabase Auth

Site em **Flask** com login no **Supabase**, papéis de acesso e aprovação de cadastros por um administrador.

Quem se cadastra entra como **associado pendente**. Um **admin** aprova o cadastro pelo painel. Só associados aprovados acessam a área restrita.

## Funcionalidades

- Cadastro e login com e-mail e senha (Supabase Auth)
- Página "Meu perfil" com nome, papel e status
- Área restrita só para associados aprovados
- Painel do admin para aprovar cadastros e mudar papéis
- Menu que muda conforme o login e o papel
- Mensagem própria para e-mail ainda não confirmado

## Tecnologias

| Parte | Ferramenta |
|---|---|
| Site (back-end) | Python, Flask |
| Páginas (front-end) | HTML, Jinja2, CSS |
| Login | Supabase Auth |
| Banco de dados | PostgreSQL (Supabase) |
| Conexão com o Supabase | supabase-py |

## Segurança

O controle de acesso fica **no banco**, não só no site. Mesmo que alguém chame o Supabase por fora do site, as regras continuam valendo.

- **RLS (Row Level Security):** cada pessoa logada vê só o próprio perfil. O admin vê todos.
- **Grant restrito:** a pessoa logada só consegue alterar o próprio nome. Papel e status ficam protegidos.
- **Função do admin:** papel e status só mudam pela função `admin_atualizar_perfil`, que confere se quem pediu é admin aprovado.
- **Visitantes sem acesso:** quem não fez login não lê a tabela de perfis.
- **Sessão assinada:** o token de login fica num cookie assinado pelo Flask, que não pode ser alterado no navegador.
- **Um cliente Supabase por requisição:** o token de uma pessoa nunca é usado no pedido de outra.
- **Chaves fora do código:** ficam no `.env`, que não vai para o GitHub. O site usa só a publishable key, nunca a secret key.

## Estrutura

```
flask-supabase-auth/
├── app.py              → rotas (páginas) e configuração do Flask
├── funcoes_banco.py    → funções que falam com o Supabase
├── templates/          → páginas HTML (Jinja2)
├── static/estilo.css   → aparência do site
├── sql/
│   ├── 001_perfis.sql      → tabela perfis e criação automática do perfil
│   └── 002_rls_perfis.sql  → regras de acesso (RLS, policies e função do admin)
├── requirements.txt    → bibliotecas e versões
└── .env.example        → modelo do arquivo de chaves
```

## Como rodar

**1. Supabase**

1. Crie um projeto em [supabase.com](https://supabase.com).
2. No **SQL Editor**, rode `sql/001_perfis.sql` e depois `sql/002_rls_perfis.sql`.
3. Para testar sem enviar e-mails: Authentication → Sign In / Providers → Email → desligue **Confirm email**.

**2. Projeto**

```
git clone https://github.com/hackelsc/flask-supabase-auth.git
cd flask-supabase-auth
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate      # Linux e macOS
pip install -r requirements.txt
```

**3. Arquivo `.env`**

Copie o `.env.example` para `.env` e preencha:

- `SUPABASE_URL`: Supabase → página inicial do projeto → Copy
- `SUPABASE_KEY`: Supabase → Project Settings → API Keys → publishable key
- `FLASK_SECRET_KEY`: gere com `python -c "import secrets; print(secrets.token_hex(32))"`

**4. Rodar**

```
python app.py
```

Abra `http://127.0.0.1:5000`.

**5. Criar o primeiro admin**

Cadastre-se pelo site. Depois, no SQL Editor do Supabase, troque o e-mail e rode:

```sql
update public.perfis
set papel = 'admin', status = 'aprovado'
where id = (select id from auth.users where email = 'seu@email.com');
```

Saia e entre de novo para o link **Admin** aparecer.

## Próximos passos

- Página **Painéis** com gráficos de dados públicos
- Mensagens de erro em vermelho
- Edição do próprio nome em "Meu perfil"

## Autora

Raquel Cardoso
