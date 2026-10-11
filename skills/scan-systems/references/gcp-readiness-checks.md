# Verificações de prontidão para o GCP

Itens 4.1 (Repositório), 4.2 (Pronto para o GCP) e 4.3 (Documentação) da cartilha de Suape (versão 2.2). Na cartilha 3.0 cada um é um documento próprio em `profile/cartilha/`, com o que procurar e o que conta como evidência. Use `grep -rn` excluindo `node_modules`, `.venv`, `dist`, `build`, `.git` e `suape-brand` (exceto onde indicado). Na falta de `grep`/`rg`, use a ferramenta de busca do runtime.

Valores do veredito, sempre um destes: `atendido`, `pendente`, `não se aplica`, `não verificado`. "Não se aplica" exige motivo (ex.: `/health` em parte que é só frontend estático).

## 4.1 Repositório

| Item | Como verificar | Pendente quando |
|---|---|---|
| Na org Complexo-Industrial-Suape | `git remote get-url origin` | remoto em conta pessoal ou sem remoto (aí: `não verificado`) |
| Nome em kebab-case | nome do remoto: `^[a-z0-9]+(-[a-z0-9]+)*$` | `_`, `.`, maiúscula |
| Branches existentes | `git branch -a` | nunca: `dev` e `hml` já existentes são aproveitadas e ligadas aos ambientes. Só registre quais existem |
| Sem segredo commitado | skill `scanning-for-hardcoded-secrets`; `git ls-files | grep -E '(^|/)\.env($|\.)' | grep -v example`; `git ls-files | grep -iE 'service.?account|credentials.*\.json|\.pem$|\.p12$'` | qualquer arquivo de segredo rastreado, ou chave no código. Se esteve no histórico, também: `git log --all --oneline -- .env` |
| `.env.example` com todos os nomes, sem valores reais | ler o arquivo e comparar com as variáveis lidas no código | ausente; falta nome que o código lê; valor real (e-mail institucional, URL de produção, ID de projeto ou instância, região diferente da usada). Placeholder genérico (`changeme`, `postgresql://user:pass@localhost/db`) está ok |
| Segredo com valor padrão no código | `grep -rnE "(environ\.get|getenv|process\.env\.[A-Z_]+ *\|\|)" ` em chaves com `SECRET`, `KEY`, `TOKEN`, `PASSWORD` | padrão literal (`"dev-secret"`, `"changeme"`): a aplicação sobe em produção com chave conhecida. Pendente **bloqueante** |
| suape-brand | ver seção própria abaixo | |

### Detecção de suape-brand

1. Submódulo: `cat .gitmodules` e `git submodule status`. Qualquer entrada com `suape-brand` = pendente.
2. Commitado: `git ls-files | grep -i 'suape-brand/'`. Qualquer arquivo = pendente.
3. Presente mas ignorado: pasta existe e `git check-ignore suape-brand` retorna o caminho = atendido.
4. Ausente: atendido se os assets usados estão numa pasta do projeto (ex.: `web/public/brand/`).

## 4.2 Pronto para o GCP

| Item | Como verificar | Pendente quando |
|---|---|---|
| Dockerfile por parte | `Dockerfile` na pasta da parte; se `docker` existir, `timeout 900 docker build` sem pedir permissão (local, sem efeito externo) | parte sem Dockerfile; Dockerfile que copia de fora do contexto (`COPY ../`) |
| Estrutura `web/ api/ docs/ infra/` | árvore do repo | front e back no mesmo repo fora desse padrão, inclusive em container único (backend na raiz + `frontend/`). Pendente **não bloqueante** |
| Porta via `PORT` | `grep -rnE 'PORT|listen\(|--port|-p [0-9]|EXPOSE|uvicorn|gunicorn|app.run' ` | porta fixa no código ou no CMD sem ler `$PORT`. Frontend servido por nginx com `listen 80` fixo também é pendente |
| Configuração por variável de ambiente | URLs, hosts, buckets literais: `grep -rnE 'https?://[a-z0-9.-]+\.(com|br|app|dev|io)|localhost:[0-9]+|\.run\.app'` | URL de API, banco ou bucket fixa em código que vai para produção |
| Health 200 | `grep -rnE "['\"]/(health|livez|readyz|healthz)['\"]"` | atendido com `/health` **ou** o par `/livez` + `/readyz`. Pendente: sem rota; só um do par; `/healthz` (o Cloud Run não repassa esse caminho ao container); health que consulta serviço externo e pode derrubar a revisão |
| Sem outro provedor de nuvem | seção própria abaixo | |
| Testes com um comando | `scripts.test` no `package.json`, `pytest` no `pyproject`, CI | sem comando, ou `"test": "echo \"Error: no test specified\""` |
| Sem CVE alta ou crítica | `pip-audit`, `npm audit --omit=dev --json` (fallbacks abaixo) | alta/crítica: pendente **bloqueante**. Média/baixa: pendente não bloqueante. Ferramenta indisponível: `não verificado` |

## 4.3 Documentação obrigatória

Ausente ou incompleta ao final da varredura = pendente **bloqueante**. Registre o estado antes e depois desta execução: o relatório e o catálogo que esta skill gera saem como "ausente antes desta varredura; gerado".

| Item | Como verificar | Incompleto quando |
|---|---|---|
| `README.md` | ler o arquivo | falta o que o projeto faz, como rodar localmente (comandos) ou como rodar os testes |
| `docs/architecture/c4-context.md` e `c4-containers.md` | `test -e`; abrir e conferir o bloco Mermaid | ausente, sem diagrama, ou diagrama que não renderiza (valide com o parser do Mermaid se houver Node) |
| `docs/systems/<repo>.md`, `docs/SYSTEMS_CATALOG.md` | gerados por esta skill | seção obrigatória do template vazia sem justificativa |
| Variáveis documentadas | comparar as leituras de ambiente no código com `.env.example`/README/relatório | qualquer variável lida no código sem nome documentado |

Não bloqueante (desatualizada): README, badge ou diagrama citando pipeline inexistente; `.env.example` com valor real ou prometendo comportamento ausente; variável documentada que o código não lê. `c4-components` e `c4-deployment` são opcionais e nunca bloqueiam.

## Os seis bloqueantes

Só estes mudam o veredito para "não pronto": (1) CVE alta/crítica ou "a confirmar"; (2) uso real de outro provedor de nuvem; (3) segredo commitado no código ou no histórico; (4) parte publicável sem Dockerfile; (5) segredo com valor padrão inseguro no código; (6) documentação obrigatória da 4.3 ausente ou incompleta ao final. Todo o resto é pendência não bloqueante. Os dois tipos viram issue.

### Detecção de outro provedor de nuvem

Procure em manifestos, lockfiles, configs de build e código. Ferramentas de IA escondem isso em `vite.config.*`, `next.config.*`, `astro.config.*` e em plugins.

| Provedor | Arquivos | Pacotes e padrões |
|---|---|---|
| Cloudflare | `wrangler.toml`, `wrangler.json*`, `.dev.vars`, `functions/`, `_worker.js`, `_routes.json` | `wrangler`, `@cloudflare/*` (incl. `@cloudflare/vite-plugin`), `miniflare`, `@opennextjs/cloudflare`, `env.DB`, `D1Database`, `R2Bucket`, `KVNamespace`, `getPlatformProxy` |
| Vercel | `vercel.json`, `.vercel/`, `api/*.ts` no formato de handler Vercel | `@vercel/*`, `@vercel/postgres`, `@vercel/blob`, `@vercel/kv`, `export const runtime = 'edge'` |
| AWS | `serverless.yml`, `template.yaml` (SAM), `amplify/`, `cdk.json` | `aws-sdk`, `@aws-sdk/*`, `boto3`, `aws-lambda`, `S3Client`, `DynamoDB`, `handler(event, context)` |
| Supabase | `supabase/`, `supabase/config.toml` | `@supabase/*`, `supabase-py`, `SUPABASE_URL`, `createClient(` com URL supabase |
| Firebase | `firebase.json`, `.firebaserc`, `firestore.rules` | `firebase`, `firebase-admin`, `firebase-functions`, `initializeApp(` |
| Outros | `netlify.toml`, `render.yaml`, `fly.toml`, `railway.json`, `Procfile` | `@netlify/*`, `@neondatabase/*`, `@planetscale/*` |

Achado em lockfile mas sem uso no código = registre como "dependência sem uso, remover" (pendente, baixo risco). Uso no código = pendente bloqueante: diga o que substitui no GCP (D1 → Cloud SQL; R2/S3/Vercel Blob → Cloud Storage; Workers/Functions/Lambda → Cloud Run; Supabase auth → a decidir com a infra).

Firebase Auth ou Google OAuth via SDK do Google não é "outro provedor" para fins de bloqueio, mas registre como integração externa.

## Armadilhas que viram pendência mesmo com o checklist "ok"

| Sinal | Por que importa no Cloud Run |
|---|---|
| SQLite (`sqlite3`, `better-sqlite3`, `sqlite:///`, `.db`) ou escrita em `/tmp`, `./uploads`, `./data` | disco efêmero: dados somem a cada reinício. Exige Cloud SQL ou Cloud Storage |
| `USER` no Dockerfile + migration/escrita em pasta criada como root | container cai ao subir. Verifique `chown` antes do `USER` |
| Migration no `CMD`/entrypoint sem lock | várias instâncias rodam a migration ao mesmo tempo. Registre como rodam hoje |
| `VITE_*`, `NEXT_PUBLIC_*`, `REACT_APP_*`, `PUBLIC_*` (Astro/SvelteKit) | valor vai para o bundle: precisa de build por ambiente e não pode ser segredo |
| CORS com origem literal (`*.run.app`, `localhost`) ou `*` com credenciais | quebra a cada URL de ambiente, ou abre a API |
| Cron em processo (`node-cron`, `APScheduler`, `setInterval` longo, `celery beat`) | Cloud Run escala para zero e para o agendamento. Precisa virar Cloud Scheduler chamando endpoint ou job |
| WebSocket/SSE, processamento longo na requisição | timeout e min-instances; avise para dimensionamento |

## Fallbacks quando falta ferramenta

| Verificação | Primária | Fallback | No relatório |
|---|---|---|---|
| CVE Python | `pip-audit -r requirements.txt` | sem pip/venv/ensurepip (comum em Python do sistema): `uv run --with pip-audit pip-audit -r requirements.txt`; projeto com `uv.lock` e sem requirements: `uv export --no-hashes > /tmp/req.txt && uv run --with pip-audit pip-audit -r /tmp/req.txt`; sem uv: `pipx run pip-audit -r requirements.txt` | sem nenhum dos três: "CVE não verificado: pip-audit indisponível" com os três comandos para o dev. Severidade: `curl -s https://api.osv.dev/v1/vulns/<ID>` (campo `severity` ou `database_specific.severity`); se for `PYSEC-*` sem severidade, repita com o alias `GHSA-*` de `aliases`. Sem dado ou sem rede = "a confirmar", bloqueante |
| CVE npm | `npm audit --omit=dev --json` (só dependências que vão para produção) | sem lockfile: `npm install --package-lock-only` não é seu papel; registre | "não verificado: sem lockfile" ou "sem rede" |
| Build da imagem | `docker build` | ler o Dockerfile linha a linha | "build não executado" |
| Testes | o comando do projeto | ler a configuração de testes e contar arquivos de teste | "não executado: exige banco" etc. |
| Cobertura | relatório existente (`coverage.xml`, `lcov.info`) ou `--coverage` | "não medida" | nunca estime porcentagem |
| Headers HTTP | configuração no código (helmet, middleware, nginx.conf) | — | "verificar na URL após provisionar" |
