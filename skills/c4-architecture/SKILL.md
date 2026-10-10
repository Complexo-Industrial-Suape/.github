---
name: c4-architecture
description: Gera a documentação de arquitetura C4 (Mermaid) exigida pela cartilha da CTIC de Suape para provisionar ambiente no GCP (Cloud Run, Cloud SQL, Secret Manager, Cloud Build). Produz docs/architecture/c4-context.md e c4-containers.md (obrigatórios), c4-deployment.md (recomendado) e c4-components-<parte>.md (quando ajudar), com cada elemento rastreado a um arquivo real do repositório e as dependências de outro provedor de nuvem (Cloudflare, Vercel, AWS, Supabase, Firebase) expostas no diagrama. Use quando o dev pedir "/c4-architecture", "documentar arquitetura", "diagrama C4", "diagrama de contexto/containers/deployment", "preparar documentação para o chamado de provisionamento", ou em inglês "architecture diagram", "C4 diagram", "system context", "container diagram", "deployment diagram", "document architecture". Use também ao atualizar o C4 depois de mudar banco, serviço externo ou parte publicável.
---

# C4 para projetos de Suape

Você documenta a arquitetura de UM repositório para o responsável pela infraestrutura da CTIC de Suape. Ele não conhece o código e não mexe em regra de negócio. Com o que você escrever, ele decide se provisiona, dimensiona o Cloud Run, cria os segredos no Secret Manager, monta o Cloud Build e abre issues no repositório quando algo impede o deploy. Ambiente único: GCP, projeto `inovacao-491419`, região `southamerica-east1`.

Seu trabalho é descrever o que o código **é**, não o que o README ou o dev dizem que é. Um diagrama bonito e errado é pior que nenhum: gera provisionamento errado e retrabalho com dinheiro público.

## Antes de desenhar, responda

- **Quais partes publicáveis existem?** Cada `Dockerfile` vira um serviço Cloud Run. Um Dockerfile que copia `web/` e `api/` (backend servindo o front compilado) é um container só. Parte sem Dockerfile é pendência, não container saudável.
- **Onde o dado mora de verdade?** Procure a string de conexão, não o nome no README. SQLite em arquivo local no Cloud Run perde tudo a cada reinício.
- **O que roda fora do GCP?** Toda chamada a Cloudflare, Vercel, AWS, Supabase, Firebase ou similar aparece no diagrama como `System_Ext` marcado. Esconder isso faz o provisionamento falhar depois.
- **O que vira segredo?** Cada variável lida pelo código. Só nomes.
- **Quando é usado?** Cron, jobs e horário de uso mudam min-instances e custo. Se o código não diz, pergunte ou marque como pendência.

## Procedimento

1. **Inventário (obrigatório, antes de qualquer diagrama).**
   **MANDATORY:** leia [references/common-mistakes.md](references/common-mistakes.md) inteiro e rode as buscas de "Varredura" dele. É lá que estão as armadilhas já vistas em Suape e os padrões que denunciam outro provedor.
   Colete, para cada container, exatamente o que as tabelas do passo 3 pedem:
   - pasta e Dockerfile; tecnologia; **porta: como o processo a recebe** (lê `PORT` ou tem número literal no `CMD`/código);
   - health: caminho real (`/health`, ou `/livez` + `/readyz`; `/healthz` é pendência);
   - banco e ORM; armazenamento de arquivos e o que acontece sem a variável do bucket;
   - integrações externas; variáveis (nome, onde é lida, build-time ou runtime);
   - rotas chamadas por agendamento e onde o agendamento é definido;
   - layout: `web/`, `api/`, `docs/`, `infra/` ou fora do padrão.
   Se existir `docs/systems/<projeto>.md` do /scan-systems, use-o como ponto de partida e confira contra o código; não copie sem conferir.
2. **Monte a tabela de rastreio.** Cada elemento que vai para um diagrama tem pelo menos um arquivo de evidência. Elemento sem evidência não entra; vira pergunta ao dev.
3. **Escreva os arquivos** em `docs/architecture/`.
   **MANDATORY:** leia [references/advanced-patterns.md](references/advanced-patterns.md) (modelos dos arquivos, com exemplos de Suape) e [references/c4-syntax.md](references/c4-syntax.md) (sintaxe e o que quebra no GitHub).
   **Do NOT load** advanced-patterns.md nem c4-syntax.md no passo 1: exemplos prontos puxam o diagrama para o exemplo, não para o código. Para só corrigir renderização de um arquivo existente, carregue apenas c4-syntax.md.
4. **Valide** com o checklist do fim. Para o Mermaid: tente `npx -y @mermaid-js/mermaid-cli -i arquivo.md -o /tmp/out.md`. Se falhar por falta de Chrome/puppeteer, valide com o parser oficial sem navegador (script em [references/c4-syntax.md](references/c4-syntax.md#validar-sem-navegador)). Sem Node nem rede, revise contra c4-syntax.md e avise o dev para conferir a pré-visualização no GitHub.
5. **Relate ao dev** as pendências que bloqueiam o chamado, em linguagem direta, com o arquivo e a correção esperada. A lista completa fica **só** em `c4-containers.md`; `c4-context.md` e `c4-deployment.md` apontam para ela.

## Arquivos de saída

| Arquivo | Quando | Responde à infra |
|---|---|---|
| `c4-context.md` | Sempre | Quem usa (servidores de Suape, público externo), com quais sistemas fala, o que está fora do GCP |
| `c4-containers.md` | Sempre | Um container por Dockerfile: pasta, Dockerfile, tecnologia, porta, banco, integrações, variáveis. **Única** lista de pendências e perguntas |
| `c4-deployment.md` | Recomendado; faça sempre que houver banco, arquivos ou cron | Cloud Run por container, Cloud SQL/Firestore/GCS, Secret Manager, Cloud Scheduler (como nó do GCP), disponibilidade esperada |
| `c4-components-<parte>.md` | Só se a parte tiver lógica que a infra ou um novo dev não entende pelo container (ex.: fila interna, worker, integração com várias etapas) | Componentes internos daquela parte |

Não crie `c4-dynamic-*` nem diagramas de código por padrão. Não tem consumidor.

## Calibragem de liberdade

- **Rígido:** nomes e caminhos dos arquivos, campos das tabelas de container e deployment, rastreio a arquivo real, exposição de outro provedor, regras de link. A infra lê isso como checklist; um campo faltando vira issue.
- **Flexível:** layout, quantidade de elementos (até ~15 por diagrama), texto da descrição, decisão de criar c4-components.
- **Proibido decidir pelo dev:** disponibilidade (24x7 ou horário comercial), tolerância a cold start, volume de usuários. Se o código e a documentação não dizem, escreva `A confirmar com o dev` e liste como pergunta.

## NEVER

- **NUNCA desenhe a partir do README ou do nome do projeto.** Em Suape já houve README alucinando a plataforma de deploy. A fonte é `package.json`, `requirements.txt`, Dockerfile, configs e código.
- **NUNCA omita dependência de outro provedor de nuvem**, nem "porque é só dev" nem "porque vai ser trocada". Já houve template Cloudflare escondido no `vite.config` (D1/R2) que só apareceu no deploy. Desenhe como `System_Ext` com "[FORA DO GCP]" no nome e liste como pendência; é isso que permite à infra abrir a issue.
- **NUNCA invente elemento, tecnologia ou porta.** Sem arquivo de evidência, não entra. Inventar faz a infra provisionar banco ou bucket que não existe.
- **NUNCA desenhe SQLite ou arquivo local como banco de produção sem alerta.** No Cloud Run o disco é efêmero; os dados somem a cada reinício ou nova revisão. Marque como pendência e indique Cloud SQL (relacional) ou Firestore/GCS conforme o uso.
- **NUNCA use caminho absoluto ou `file:///`** (`/home/...`, `C:\Users\...`). Quebra para todos fora da máquina do dev. Links relativos a partir de `docs/architecture/`, ex.: `[api/Dockerfile](../../api/Dockerfile)`.
- **NUNCA escreva valor de segredo**, nem exemplo realista. Só o nome da variável. O valor vai por canal seguro direto ao Secret Manager.
- **NUNCA trate `VITE_*`/`NEXT_PUBLIC_*` como variável de runtime.** Elas entram no bundle no build; trocar valor exige rebuild por ambiente. Registre na tabela como "build-time".
- **NUNCA desenhe URL fixa do Cloud Run** (`*.run.app`) como integração entre web e api. Se o código tem a URL ou o CORS depende dela, é pendência: cada ambiente gera outra URL.
- **NUNCA use setas "usa", "chama", "conecta".** Toda seta tem ação + protocolo: `Rel(web, api, "Envia pedido de manutenção", "HTTPS/JSON")`.
- **NUNCA desenhe `cloudbuild.yaml`, Terraform ou pipeline como container.** Isso é da infra, não do projeto.
- **NUNCA desenhe o Cloud Scheduler como `System_Ext`.** É recurso do GCP que a infra cria. No c4-containers ele é `Container_Ext(scheduler, "Cloud Scheduler [GCP]", "Cloud Scheduler", "...")`, origem da seta para a rota agendada; o detalhe (frequência, autenticação) vai no c4-deployment. Se o agendamento não está definido no repositório, escreva "A confirmar com o dev" em vez de inventar horário.
- **NUNCA desenhe o banco de outro sistema de Suape como banco deste projeto.** Leitura de um banco que pertence a outro sistema (credencial própria, variável do tipo `OUTRO_DATABASE_URL`) é `SystemDb_Ext(alias, "Banco do <sistema dono>", "...")`. Registre a dependência e a permissão necessária como pergunta ao dev: a infra precisa liberar o acesso entre projetos e saber quem é o dono do dado.
- **NUNCA ponha na tabela de variáveis uma variável que só existe no `.env.example`.** Se o código não a lê, a infra criaria um segredo inútil. Vira pendência de documentação não bloqueante ("variável documentada e não usada").
- **NUNCA aceite `ENV PORT` no Dockerfile como prova de que o app lê `PORT`.** O que vale é o `CMD`/`ENTRYPOINT` e o código. Exemplo: `ENV PORT=8080` junto com `CMD gunicorn --bind 0.0.0.0:8080` ignora a porta que o Cloud Run injeta.
- **NUNCA repita a lista de pendências em mais de um arquivo.** Três cópias divergem na primeira correção; a infra abre issue a partir de uma lista só.

## Pendências que você sempre verifica

Cada uma vira linha em "Pendências para o provisionamento" de `c4-containers.md`, com arquivo e correção:
sem Dockerfile numa parte publicável; segredo com valor padrão inseguro no código; porta literal no `CMD`/código (mesmo com `ENV PORT`); sem health que responda 200 (`/health`, ou `/livez` + `/readyz`) ou uso de `/healthz`; configuração fixa no código (URL, bucket, credencial); fallback para disco local quando falta variável; segredo commitado (`.env` real, chave JSON de service account); dependência de outro provedor; banco efêmero; `USER` não-root sem `chown` dos diretórios que a migração ou o app escrevem; CORS amarrado a URL gerada; `suape-brand` como submódulo ou kit commitado em vez de `.gitignore`; frontend e backend no mesmo repo fora de `web/` e `api/`, inclusive com um único container (não bloqueante).

**Severidade (coluna "Bloqueia?").** Bloqueantes (6): (1) vulnerabilidade alta ou crítica em dependência; (2) uso real de outro provedor de nuvem; (3) segredo commitado (no código ou no histórico); (4) parte publicável sem Dockerfile; (5) segredo com valor padrão inseguro no código (ex.: `os.environ.get("SECRET_KEY", "dev-...")`); (6) documentação exigida pela cartilha (3.3) **ausente ou incompleta**: `README.md` sem o que o projeto faz, como rodar localmente ou como rodar os testes; `docs/architecture/c4-context.md` ou `c4-containers.md` faltando, sem seção obrigatória ou com diagrama que não renderiza; `docs/systems/<repo>.md` ou `docs/SYSTEMS_CATALOG.md` faltando; variável lida pelo código sem estar documentada por nome. Todo o resto é pendência não bloqueante, inclusive documentação **desatualizada ou incorreta** (README citando pipeline inexistente, badge quebrado, `.env.example` com valor real ou prometendo comportamento ausente, variável documentada que o código não lê). `c4-components` e `c4-deployment` não bloqueiam. Bloqueante e não bloqueante viram issue.

**Antes e depois.** Esta skill gera parte da documentação que ela mesma cobra. Registre o estado de cada item da regra 6 **antes** da execução ("ausente antes desta varredura") e **depois**. A pendência bloqueante só fica se, ao terminar, algo continuar ausente ou incompleto: `c4-context.md`/`c4-containers.md` que não deu para gerar completos por falta de informação, falta de README, falta do relatório do /scan-systems (`docs/systems/<repo>.md`, `docs/SYSTEMS_CATALOG.md`, que são de outra skill) ou variável lida no código sem documentação.
Esta skill não roda auditoria de dependências: se `docs/systems/<projeto>.md` (do /scan-systems) registra vulnerabilidade alta ou crítica, copie a linha como bloqueante; se não há relatório, escreva "Auditoria de dependências: não verificada, rode /scan-systems".

Não são pendência: branches `dev`/`hml` já existentes; `USER` não-root com `chown` correto; serviços Google (Gemini, Drive, Vision) como integração externa.

Não corrija o código por conta própria: esta skill documenta. Se o dev pedir a correção, faça em outra etapa.

## Checklist antes de entregar

- [ ] `c4-context.md` e `c4-containers.md` existem; deployment existe se houver banco, arquivos ou cron.
- [ ] Pendências e perguntas só em `c4-containers.md`; os outros arquivos têm o link para lá.
- [ ] Todo elemento tem nome, tecnologia e descrição; toda seta tem ação + protocolo.
- [ ] Toda linha das tabelas tem link relativo para um arquivo que existe (`test -e` a partir da raiz).
- [ ] Nenhum `/home/`, `C:\`, `file://` nos arquivos gerados (`grep -rnE 'file://|/home/|[A-Z]:\\' docs/architecture`).
- [ ] Toda dependência fora do GCP aparece no diagrama e nas pendências.
- [ ] Lista de variáveis completa, só nomes, com build-time separado de runtime, e só variáveis que o código lê.
- [ ] Toda pendência tem a coluna "Bloqueia?" preenchida conforme a regra de severidade (6 bloqueantes).
- [ ] Regra 6 conferida no fim: README, os dois C4 obrigatórios, relatório do /scan-systems e catálogo, com estado antes/depois; o que continuar ausente ou incompleto está como bloqueante.
- [ ] Mermaid sem os recursos que o GitHub não renderiza (ver c4-syntax.md).
- [ ] Nada decidido pelo dev sem marca "A confirmar com o dev".
