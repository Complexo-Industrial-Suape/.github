# Inventário e armadilhas de Suape

MANDATORY no passo 1. Contém a varredura e as falhas reais já vistas na CTIC. Não carregue para só ajustar layout de um diagrama existente.

## Varredura

Rode a partir da raiz do repositório. Os comandos usam `grep` e `find`, que existem em qualquer ambiente. Com `rg` instalado, troque `grep -rnE ... $EXC` por `rg -n ...` (ele já ignora o `.gitignore`).

```bash
EXC="-I --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv --exclude-dir=venv --exclude-dir=dist --exclude-dir=build --exclude-dir=tests --exclude-dir=test --exclude=*lock*"
# -I ignora binários; tests/ fora para não confundir mock com uso real (abra os testes só para confirmar comportamento)

# 1. partes publicáveis e layout
find . -name Dockerfile -not -path '*/node_modules/*' -not -path './.git/*'
ls -d web api docs infra frontend backend 2>/dev/null
grep -nE '^(FROM|COPY|ENV PORT|EXPOSE|USER|CMD|ENTRYPOINT)' $(find . -name Dockerfile -not -path '*/node_modules/*')

# 2. outro provedor de nuvem: arquivos de config
ls wrangler.toml wrangler.json* vercel.json netlify.toml firebase.json .firebaserc serverless.yml amplify.yml fly.toml railway.json render.yaml supabase/config.toml 2>/dev/null
# 3. outro provedor de nuvem: SDKs e imports (não palavras soltas)
grep -rnE "boto3|botocore|@aws-sdk/|aws-sdk|aws-lambda|serverless-http|wrangler|@cloudflare/|miniflare|@vercel/|@netlify/|@supabase/|supabase-js|from supabase|firebase-admin|firebase/(app|firestore|storage|auth)|@planetscale/|@neondatabase/" $EXC .
grep -nE '^\s*\[\[(d1_databases|r2_buckets|kv_namespaces)\]\]|"(d1_databases|r2_buckets)"' wrangler.* 2>/dev/null

# 4. banco e armazenamento
grep -rnE "DATABASE_URL|sqlite|better-sqlite3|postgres|psycopg|pg8000|mysql|mongo|prisma|sequelize|typeorm|sqlalchemy|drizzle|cloud.sql|google-cloud-storage|UPLOAD" $EXC . | head -60

# 5. variáveis
cat .env.example 2>/dev/null
grep -rnoE "process\.env\.[A-Z_]+|import\.meta\.env\.[A-Z_]+|os\.environ(\.get)?\(?\[?['\"][A-Z_]+|getenv\(['\"][A-Z_]+" $EXC . | sort -u

# 6. configuração fixa e segredos commitados
grep -rnE "\.run\.app|localhost:[0-9]+" $EXC --exclude=*.md .
git ls-files | grep -iE '(^|/)\.env$|service.?account.*\.json|credentials.*\.json|\.pem$|\.key$'

# 7. porta, health, cron
grep -rnE "PORT|listen\(|bind|/health|/livez|/readyz|/healthz" $EXC --exclude=*.md . | head -40
grep -rnE "cron|schedule|setInterval|APScheduler|celery beat|X-Tasks|X-CloudScheduler" $EXC --exclude=*.md . | head -20

# 8. marca
cat .gitmodules 2>/dev/null; git ls-files | grep -c 'suape-brand/'; grep -n 'suape-brand' .gitignore
```

**Um acerto é indício, não prova.** Abra cada arquivo citado antes de afirmar. Em especial no item 3: `firebase` pode ser só o `firebase-tools` em devDependency de um script antigo; `@cloudflare/` pode estar só na documentação do `suape-brand` (link de CDN). Só registre outro provedor quando o código de produção, o build ou a configuração de deploy dependem dele.

## Como interpretar o que achou

| Achado | Veredito |
|---|---|
| `ENV PORT=8080` no Dockerfile, mas `CMD`/`ENTRYPOINT` com porta literal (`--bind 0.0.0.0:8080`, `--port 8000`, `app.listen(3000)`) | **Pendência.** O Cloud Run injeta `PORT`; o `ENV` é só padrão e o comando o ignora. Correção: `--bind 0.0.0.0:$PORT` (forma shell) ou ler `PORT` no código |
| `/health` respondendo 200, ou o par `/livez` + `/readyz` | Atendido. Registre o caminho real na tabela |
| `/healthz` | **Pendência.** O Cloud Run não repassa esse caminho para o container: o check sempre falha |
| Frontend e backend no mesmo repo fora de `web/` e `api/` (ex.: backend na raiz + `frontend/`) | **Pendência não bloqueante**, mesmo com um único container. Correção: mover para `web/` e `api/`; um único Dockerfile copia as duas pastas |
| Branches `dev`/`hml` já existem | Não é pendência: são aproveitadas no provisionamento |
| Fallback para disco local quando falta variável (ex.: upload em `./uploads` sem `UPLOADS_BUCKET`) | Pendência: no Cloud Run esse caminho é efêmero. Correção: falhar na inicialização sem a variável |
| URL de produção como valor padrão no código | Pendência: cada ambiente tem outra URL. Correção: variável obrigatória |
| Valor real de e-mail, região ou projeto no `.env.example` | Pendência leve: o exemplo deve ter placeholder |
| Variável no `.env.example` que o código não lê | Fora da tabela de variáveis. Pendência de documentação não bloqueante |
| Variável lida pelo código e ausente da documentação | **Bloqueante** (regra 6): sem o nome, a infra não cria o segredo e o serviço sobe quebrado |
| README sem o que faz, como rodar localmente ou como testar; C4 obrigatório ou relatório /scan-systems ausente ou incompleto | **Bloqueante** (regra 6). Registrar estado antes e depois desta execução |
| README citando pipeline inexistente, badge quebrado | Pendência não bloqueante (documentação desatualizada) |
| `os.environ.get("SECRET_KEY", "valor-fixo")` ou equivalente | **Bloqueante**: se a variável faltar em produção, o app sobe com segredo conhecido. Correção: falhar na inicialização sem a variável |
| Variável apontando para o banco de outro sistema (ex.: `<OUTRO>_DATABASE_URL`) | `SystemDb_Ext` com o nome do sistema dono + pergunta ao dev sobre a permissão de acesso |

## Falhas reais em Suape e como registrar

| Falha vista | Onde se esconde | Como registrar |
|---|---|---|
| Projeto gerado por IA com template Cloudflare | `vite.config.*` com `@cloudflare/vite-plugin`, `[[d1_databases]]`/`[[r2_buckets]]` em `wrangler.*`, `npm start` chamando `wrangler` | `System_Ext` "[FORA DO GCP] Cloudflare D1" + pendência "migrar para Cloud SQL/GCS" |
| README alucinando a plataforma | README fala em Vercel/Railway sem config correspondente, ou fala em GCP com `vercel.json` presente | Descreva o código; cite a divergência nas pendências |
| SQLite em `/tmp` ou arquivo local | `DATABASE_URL=sqlite:///`, `better-sqlite3` | `ContainerDb` "SQLite em disco efêmero: perde dados no reinício" + pendência |
| `USER` não-root quebrando migração | `USER app` antes de migração que escreve em pasta do root, sem `chown` | Pendência citando a linha do Dockerfile. `USER` com `chown` antes está correto |
| `VITE_*` embutido no build | `import.meta.env.VITE_API_URL` | Variável "build-time, exige rebuild por ambiente" |
| CORS dependente da URL gerada | `origin` fixo com `*.run.app` | Pendência: origem por variável de ambiente |
| Links `file:///` e caminhos absolutos | docs geradas por IA | Nunca reproduza; use link relativo |
| `suape-brand` submódulo ou commitado | `.gitmodules`, pasta versionada | Pendência: copiar só os assets usados para `web/public/brand/` e pôr `suape-brand/` no `.gitignore` |

## Erros de modelagem que a infra sente

- **Container é o que vira imagem e serviço Cloud Run.** Biblioteca compartilhada, pasta `shared/`, ORM e store do frontend não são containers. Parte sem Dockerfile é pendência ou componente.
- **Um Dockerfile que copia `web/` e `api/`** (backend servindo o front compilado) é **um** container. Descreva os dois papéis na descrição; não invente dois.
- **Banco gerenciado é `ContainerDb` no nível 2**: a infra precisa saber que tem de criá-lo.
- **APIs de terceiros são `System_Ext`**, sem detalhe interno. Serviços Google (Gemini, Drive, Vision, Gmail) também são externos, mas não são "outro provedor": não marque como fora do GCP; liste a credencial que exigem.
- **Cloud Scheduler é recurso do GCP, não sistema externo.** Nunca `System_Ext`. No containers: `Container_Ext(scheduler, "Cloud Scheduler [GCP]", "Cloud Scheduler", "Dispara a rota agendada")` com `Rel(scheduler, api, "Chama POST /rota", "HTTPS + OIDC ou token")`. No deployment, é um `Deployment_Node` do GCP com frequência e autenticação.
- **Banco de outro sistema de Suape** lido com credencial própria é `SystemDb_Ext`, nunca `ContainerDb` deste projeto. Se a rota existe no código mas não há definição do agendamento no repositório (horário, quem dispara), escreva "Agendamento: A confirmar com o dev".
- **Job com Dockerfile ou entrypoint próprio** é container (Cloud Run Job).
- **Réplicas, região e min-instances** não entram no containers. Vão no c4-deployment.
