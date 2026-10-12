# Pronto para o GCP: arquitetura, contêineres e Cloud Run

[← Voltar ao catálogo da cartilha](../README.md)

No Google Cloud, os sistemas de Suape rodam no **Cloud Run** (serviço serverless gerenciado), com bancos no **Cloud SQL** ou **Firestore**, arquivos no **Cloud Storage (GCS)** e credenciais no **Secret Manager**.

Para que uma aplicação suba de forma automática pelo Cloud Build e rode com estabilidade, ela precisa atender aos padrões abaixo.

---

## 1. Aplicações sem estado (Stateless)

Instâncias do Cloud Run são descartáveis. Elas sobem sob demanda, escalam com o tráfego e desligam quando não há requisições.

* **Não salve dados no disco local:** Pastas como `./uploads` ou bancos SQLite locais (`sqlite:////tmp/app.db`) somem sempre que uma instância reinicia ou escala.
* **Uploads e arquivos:** Envie arquivos (fotos, PDFs, relatórios) direto para buckets do Cloud Storage usando a biblioteca oficial (`google-cloud-storage`).
* **Sessões de usuário:** Salve sessões no banco de dados ou use tokens JWT assinados, sem depender de memória local compartilhada entre requisições.

---

## 2. Dockerfiles para produção

Cada parte publicável da aplicação (backend, frontend ou worker) precisa do seu próprio `Dockerfile`.

### Boas práticas de contêiner

1. **Multi-Stage Build:**
   Separe o estágio de compilação do estágio final de execução. Imagens enxutas diminuem o tempo de upload no Artifact Registry e aceleram o início das instâncias no Cloud Run.
2. **Usuário comum (`appuser`):**
   Contêineres não devem rodar como `root`. Crie um usuário de sistema:
   ```dockerfile
   RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
   USER appuser
   ```
3. **Escuta dinâmica na porta `$PORT`:**
   O Cloud Run injeta a variável `PORT` (padrão 8080) na inicialização. A aplicação precisa escutar nessa porta.
   * **FastAPI / Uvicorn:**
     ```dockerfile
     CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
     ```
   * **Flask ou Django com Gunicorn:**
     ```dockerfile
     CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 app:app"]
     ```
   * **Erro comum:** Fixar `0.0.0.0:8080` no comando sem ler a variável `PORT`.

---

## 3. Rotas de verificação de saúde (Health Check)

O Cloud Run testa a saúde das instâncias com requisições HTTP periódicas. Se o contêiner não responder 200 OK no tempo limite, o deploy é cancelado e o tráfego não é liberado.

* **Rotas aceitas:**
  * `/health` respondendo `{"status": "ok"}` e HTTP 200.
  * O par `/livez` e `/readyz` respondendo HTTP 200.
* **Não use `/healthz`:** Essa rota específica é consumida pela infraestrutura de rede do Google e não chega até o seu contêiner, gerando falhas falsas no deploy.

---

## 4. Desacoplamento de provedor de nuvem

Projetos de Suape rodam no GCP. Se o código veio de templates prontos ou geradores de IA, é comum que traga configurações da Cloudflare, Vercel, AWS ou Supabase. Adapte esses pontos antes de pedir o ambiente.

| Serviço externo comum | O que faz | Substituto no GCP |
|---|---|---|
| Cloudflare Workers ou Wrangler | Execução serverless em V8 | Servidor Node ou Python em contêiner no Cloud Run |
| Cloudflare D1 | Banco SQLite em nuvem | PostgreSQL no Cloud SQL |
| Cloudflare R2 ou AWS S3 | Armazenamento de objetos | Google Cloud Storage (GCS) |
| Vercel Serverless Functions | Endpoints serverless | Cloud Run com FastAPI ou Flask |
| Supabase Auth ou Firebase Auth | Autenticação gerenciada | Google OIDC institucional ou JWT próprio |
| AWS Lambda | Funções sob demanda | Cloud Run ou Cloud Run Jobs |

Antes do chamado, confira no `package.json`, `pyproject.toml` e arquivos de configuração se não há sobras de `wrangler`, `boto3`, `@supabase/supabase-js` ou `firebase-admin`.

---

## 5. Variáveis de ambiente e segredos

A aplicação precisa ser configurada sem reconstruir a imagem:

* **Backend:** Valores são lidos em tempo de execução via variáveis de ambiente normais ou puxados do **Secret Manager**.
* **Frontend (`VITE_*`):** O Vite grava essas variáveis no código compilado durante o build (`npm run build`). Elas são públicas por definição. Chaves de API privadas e senhas nunca podem ficar no frontend.

---

## 6. Segurança e testes

O Cloud Build roda verificações antes de publicar qualquer imagem:

1. **Testes automatizados com um comando:**
   * Python: `uv run pytest` ou `pytest tests/ -v`
   * Frontend: `npm run lint && npm run test`
   * Se um teste falhar, o deploy para imediatamente.
2. **Auditoria de dependências:**
   * Não publicamos código com vulnerabilidades **altas** ou **críticas**.
   * Teste na sua máquina:
     ```bash
     # Backend Python
     uv run --with pip-audit pip-audit -r requirements.txt
     
     # Frontend Node
     npm audit --omit=dev
     ```

---

## Checklist técnico

Confirme estes pontos antes de pedir o ambiente:

- [ ] Dockerfile funcional para cada parte publicável.
- [ ] Contêiner rodando com usuário comum (`appuser`).
- [ ] Aplicação escutando na porta dinâmica `${PORT:-8080}`.
- [ ] Rota de saúde em `/health` ou `/livez` e `/readyz` (evite `/healthz`).
- [ ] Zero persistência em disco local efêmero (`./uploads` ou SQLite).
- [ ] Nenhuma dependência proprietária de AWS, Cloudflare, Vercel ou Supabase.
- [ ] Testes passando localmente.
- [ ] Zero vulnerabilidades altas ou críticas no `pip-audit` e `npm audit`.
