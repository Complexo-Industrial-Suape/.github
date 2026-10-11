# Pronto para o GCP

[← Voltar ao catálogo da cartilha](../README.md)

O pedido de ambiente só segue quando todos os itens abaixo estiverem atendidos.

- [ ] O projeto usa a stack padrão ([stack padrão](02-stack-padrao.md)) ou tem a exceção justificada no chamado.
- [ ] Cada parte publicável (API, frontend, job) tem um `Dockerfile` que funciona com `docker build .`.
- [ ] Se frontend e backend estão no mesmo repositório, a estrutura é esta, mesmo que o projeto rode num único container. Nesse caso, um só `Dockerfile` copia as duas pastas para dentro da imagem.
  ```
  meu-projeto/
  ├── web/     frontend React/Vite
  ├── api/     backend Python
  ├── docs/    documentação (C4 + Scan Systems)
  └── infra/   só se precisar (Terraform, scripts)
  ```
- [ ] A aplicação escuta na porta da variável `PORT`. O Cloud Run usa 8080 por padrão.
- [ ] Toda configuração vem de variáveis de ambiente. URL, credencial e nome de bucket não ficam fixos no código.
- [ ] A API tem um endpoint de saúde que responde 200: `/health`, ou o par `/livez` e `/readyz`. Evite `/healthz`, porque o Cloud Run não repassa esse caminho para o container.
- [ ] O projeto não depende de outro provedor de nuvem. Projetos gerados por ferramentas de IA ou por templates costumam trazer Cloudflare, Vercel, AWS, Supabase ou Firebase escondidos (`wrangler`, D1, R2, Vercel Functions, Lambda, S3). Confira o `package.json`, os arquivos de configuração e o README antes de abrir o chamado.
- [ ] Os testes automatizados rodam com um comando (`pytest`, `npm run test`).
- [ ] Não há vulnerabilidade alta ou crítica nas dependências. Rode `pip-audit` (ou `uv run --with pip-audit pip-audit`) e `npm audit --omit=dev`. Vulnerabilidade alta ou crítica bloqueia o provisionamento e vira issue até ser corrigida.
