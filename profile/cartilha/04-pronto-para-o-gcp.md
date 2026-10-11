# Pronto para o GCP: arquitetura, contêineres e boas práticas

[← Voltar ao catálogo da cartilha](../README.md)

No Google Cloud, os sistemas de Suape rodam primariamente no **Cloud Run** (serviços serverless gerenciados), com persistência em **Cloud SQL** ou **Firestore**, arquivos no **Cloud Storage (GCS)** e segredos no **Secret Manager**. 

Para que sua aplicação escale com estabilidade e seja implantada de forma 100% automatizada pelo Cloud Build, ela precisa atender aos padrões de engenharia descritos abaixo.

---

## 1. Princípio fundamental: Aplicações Stateless (12-Factor)

Instâncias do Cloud Run são efêmeras. Elas são criadas sob demanda, escalam horizontalmente com aumento de tráfego e escalam até zero quando o sistema fica ocioso.

* **Não use o disco local para armazenar dados:** Pastas locais como `./uploads` ou bancos em arquivo (`sqlite:////tmp/app.db`) são descartadas a cada reinício ou criação de nova instância.
* **Armazenamento de arquivos:** Envie uploads (fotos, relatórios, PDFs, anexos) diretamente para buckets do Google Cloud Storage utilizando a SDK oficial (`google-cloud-storage`).
* **Sessões e estado:** Armazene sessões de usuário em banco de dados ou adote autenticação stateless via tokens JWT assinados.

---

## 2. Dockerfiles prontos para produção

Cada parte publicável da aplicação (backend, frontend ou worker) deve ter seu próprio `Dockerfile`.

### Boas práticas de containerização

1. **Multi-Stage Build:**
   Separe o estágio de compilação/instalação do estágio final de execução. Isso reduz o tamanho da imagem de centenas de megabytes para dezenas, acelerando o push/pull no Artifact Registry e o cold start do Cloud Run.
2. **Usuário não-root (`appuser`):**
   Por segurança, contêineres nunca devem rodar como `root`. Crie um usuário de sistema e aplique as permissões adequadas:
   ```dockerfile
   RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
   USER appuser
   ```
3. **Escuta dinâmica na porta `$PORT`:**
   O Cloud Run injeta a variável de ambiente `PORT` (por padrão 8080) na inicialização do contêiner. O servidor de aplicação deve obrigatoriamente escutar nessa porta dinâmica.
   * **Correto (Uvicorn / FastAPI):**
     ```dockerfile
     CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
     ```
   * **Correto (Gunicorn / Flask / Django):**
     ```dockerfile
     CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 app:app"]
     ```
   * **Anti-pattern a evitar:** Chamar `gunicorn --bind 0.0.0.0:8080` de forma fixa ignorando a variável `PORT`.

---

## 3. Contrato de Health Check e Sondas de Vida

O Cloud Run monitora a saúde das instâncias através de sondas HTTP. Se o contêiner falhar em responder 200 OK dentro do timeout, o tráfego é cancelado e o deploy falha.

* **Endpoints homologados:**
  * Opção 1: `/health` respondendo `{"status": "ok"}` e HTTP 200.
  * Opção 2: O par `/livez` (liveness) e `/readyz` (readiness) respondendo HTTP 200.
* **Proibido usar `/healthz`:** O caminho específico `/healthz` é interceptado e consumido pela infraestrutura interna de rede do GCP/Google Front End e não chega ao contêiner da aplicação, gerando falsos negativos no deploy.

---

## 4. Desacoplamento de nuvem (Sem Vendor Lock-in)

Projetos desenvolvidos em Suape rodam no Google Cloud. Se o projeto foi gerado por templates ou ferramentas de IA, é muito comum que venha configurado para serviços da Cloudflare, Vercel, AWS ou Supabase. **Isso deve ser adaptado antes do chamado.**

| Tecnologia externa | O que faz | Substituto oficial no GCP |
|---|---|---|
| Cloudflare Workers / Wrangler | Servidor serverless em V8 | Servidor Node.js em container no Cloud Run |
| Cloudflare D1 | Banco relacional SQLite | PostgreSQL no Cloud SQL |
| Cloudflare R2 / AWS S3 | Object Storage | Google Cloud Storage (GCS) |
| Vercel Serverless Functions | Endpoints serverless | Cloud Run com FastAPI / Flask |
| Supabase Auth / Firebase Auth | Autenticação gerenciada | Google OIDC institucional / JWT próprio |
| AWS Lambda | Funções sob demanda | Cloud Run / Cloud Run Jobs |

Antes de abrir o chamado, confira no `package.json`, `pyproject.toml` e arquivos de configuração se não há referências a `wrangler`, `boto3`, `@supabase/supabase-js` ou `firebase-admin`.

---

## 5. Variáveis de ambiente e segredos

Toda a configuração da aplicação deve ser parametrizável sem necessidade de reconstruir a imagem:

* **Variáveis de Backend:** Injetadas em runtime pelo Cloud Run a partir de variáveis de ambiente do serviço ou mapeadas de segredos do **Secret Manager**.
* **Variáveis de Frontend (`VITE_*`):** O Vite embute essas variáveis no código estático durante o comando `npm run build`. Por isso, URLs de API e chaves públicas de mapa são injetadas como `--build-arg` durante a montagem do container no Cloud Build. Nunca coloque credenciais privadas em variáveis de frontend.

---

## 6. Segurança de dependências e testes

O Cloud Build executa a suíte de validação antes de construir e publicar as imagens:

1. **Testes automatizados com um comando:**
   * Python: `uv run pytest` ou `pytest tests/ -v`
   * Frontend: `npm run lint && npm run test`
   * Se os testes falharem, o deploy é imediatamente abortado, protegendo os ambientes.
2. **Auditoria de CVEs:**
   * Nenhum sistema sobe para o GCP com vulnerabilidades classificadas como **ALTAS** ou **CRÍTICAS**.
   * Teste localmente antes de submeter:
     ```bash
     # Backend Python
     uv run --with pip-audit pip-audit -r requirements.txt
     
     # Frontend Node
     npm audit --omit=dev
     ```

---

## Checklist técnico do GCP

Confirme todos os pontos antes de solicitar provisionamento:

- [ ] Dockerfile funcional na raiz ou nas pastas `web/` e `api/`.
- [ ] O contêiner roda como usuário não-root (`appuser`).
- [ ] O servidor escuta na porta dinâmica especificada por `${PORT:-8080}`.
- [ ] Endpoint de saúde ativo em `/health` ou `/livez` e `/readyz` (sem usar `/healthz`).
- [ ] Nenhuma persistência de dados em disco local (`./uploads` ou SQLite).
- [ ] Sem bibliotecas ou dependências proprietárias de AWS, Cloudflare, Vercel ou Supabase.
- [ ] Testes automatizados executando e passando localmente.
- [ ] Zero vulnerabilidades altas ou críticas em `pip-audit` e `npm audit`.
