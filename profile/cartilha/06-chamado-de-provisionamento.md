# Chamado de provisionamento

[← Voltar ao catálogo da cartilha](../README.md)

Antes de abrir o chamado, confira o [repositório](03-repositorio.md), o que precisa estar [pronto para o GCP](04-pronto-para-o-gcp.md) e a [documentação](05-documentacao.md).

## Como abrir

Mande um e-mail para **raulsilva@suape.pe.gov.br** com o assunto `Provisionamento de ambiente GCP - <nome-do-repositório>`. Exemplo: `Provisionamento de ambiente GCP - rdo-suape-api`.

A confirmação chega por e-mail. Se precisar de um contato mais rápido, peça na própria mensagem.

### Modelo do e-mail

```text
Assunto: Provisionamento de ambiente GCP - <nome-do-repositório>

1. Projeto
   - Repositório: https://github.com/Complexo-Industrial-Suape/<repo>
   - Responsável (nome e contato):
   - Área/cliente demandante:
   - O que o sistema faz (2 a 3 frases):

2. Público e uso
   - Quem usa: ( ) só servidores de Suape  ( ) público externo  ( ) os dois
   - Usuários esperados (número aproximado):
   - Precisa de login? Qual (Google institucional, usuário e senha, outro)?

3. Disponibilidade
   - Horário de uso: ( ) só horário comercial  ( ) 24x7
   - Precisa estar no ar fora do horário comercial? Por quê?
   - Aceita alguns segundos de lentidão no primeiro acesso do dia (cold start)? ( ) sim  ( ) não
   - Impacto se ficar fora do ar por 1 hora:

4. Técnica
   - Stack: ( ) padrão (Python 3.14 + FastAPI/Flask/Django, React c/ Vite ou Astro, banco PostgreSQL/MongoDB)
   - Se outra stack, comprovação de restrição técnica:
   - Partes publicáveis (API, frontend, job) e a pasta de cada uma:
   - Banco de dados: ( ) nenhum  ( ) PostgreSQL  ( ) MongoDB  ( ) outro:
   - Volume de dados estimado:
   - Armazenamento de arquivos (fotos, PDFs, uploads)? Volume estimado:
   - Integrações externas (APIs de terceiros, Google Drive, Gemini, e-mail, SMS):
   - Tarefas agendadas (cron) e frequência:
   - Variáveis de ambiente e segredos: ver docs/systems/<projeto>.md

5. Prazos
   - Data desejada para hml:
   - Data desejada para produção:

6. Checklist (documentos Repositório e Pronto para o GCP da cartilha)
   ( ) Repositório na org, nome no padrão, sem segredos commitados
   ( ) Commits assinados (Verified no GitHub)
   ( ) Stack padrão ou exceção justificada
   ( ) Dockerizado, configuração por variáveis de ambiente, endpoint de saúde
   ( ) Sem vulnerabilidade alta ou crítica nas dependências
   ( ) Sem dependência de outro provedor de nuvem
   ( ) Identidade Visual: splash screen integrada, logos da CCOM e sem submódulo (ver documento 09)
   ( ) Documentação C4 e Scan Systems no repositório
```

As seções 2 e 3 do e-mail decidem quanto o projeto vai custar. Um sistema interno usado só em horário comercial pode desligar quando ninguém está usando e sai quase de graça. Um sistema público 24x7 precisa de instância ligada o tempo todo. Responda com sinceridade, porque superdimensionar custa dinheiro público.

## Depois do chamado

1. Você recebe a confirmação de que o pedido chegou.
2. O repositório e a documentação são inspecionados.
3. Se algo impedir o provisionamento, você recebe issues no repositório e um resumo na resposta do e-mail. Os casos mais comuns são projeto sem Dockerfile, dependência de outro provedor, documentação incompleta e segredo commitado. Corrija e responda o mesmo e-mail, que a inspeção recomeça.
4. Com tudo certo, a infraestrutura cria:
   - os ambientes dev, hml e prod no GCP, dimensionados conforme o chamado;
   - as branches `dev` e `hml` a partir da `main`, ou aproveita as que já existem;
   - os segredos no Secret Manager, com valores combinados com você por canal seguro (nunca por e-mail);
   - o deploy automático pelo Cloud Build (`cloudbuild.yaml`).
5. Vocês combinam o CI (quais testes rodam antes do deploy), os ciclos de entrega, as rotinas e os cron jobs.
6. Você recebe um resumo com a URL de cada ambiente, os gatilhos de deploy, os nomes dos segredos e onde acompanhar os builds.

O `cloudbuild.yaml` é infraestrutura, e só o responsável pela infraestrutura altera esse arquivo. Precisa mudar algo no pipeline? Peça por e-mail.
