# Papéis, responsabilidades e ciclo de vida do projeto

[← Voltar ao catálogo da cartilha](../README.md)

O objetivo desta governança é direto: **dar a César o que é de César.**

Um desenvolvedor de software precisa ter autonomia e responsabilidade técnica sobre o ciclo de vida do seu código: domínio de Git, controle de branches, containerização, testes e documentação de arquitetura. Da mesma forma, a infraestrutura precisa garantir estabilidade, segurança, rastreabilidade e controle rigoroso de custos de nuvem pública.

Para eliminar atritos e retrabalho, os papéis e o fluxo de projetos novos funcionam de maneira previsível.

---

## 1. Matriz de responsabilidades

| Responsabilidade | Desenvolvedor do Projeto | Responsável pela Infraestrutura (Raul César) |
|---|:---:|:---:|
| Criação do repositório na organização | **Dono** | Permissões de org |
| Desenvolvimento do MVP e regras de negócio | **Dono exclusivo** | *Não interfere* |
| Escolha e implementação dos testes automatizados | **Dono** | Validação no pipeline |
| Criação e manutenção dos Dockerfiles | **Dono** | Consumo no build |
| Elaboração da documentação técnica (C4 e Scan Systems) | **Dono** | Auditoria e inspeção |
| Assinatura digital de commits com chave SSH | **Dono** | Fiscalização de conformidade |
| Abertura formal do chamado de provisionamento | **Dono** | Avaliação e resposta |
| Criação dos ambientes no Google Cloud (dev, hml, prod) | *Não executa* | **Dono exclusivo** |
| Criação das branches oficiais (`dev` e `hml`) no Git | *Não executa* | **Dono exclusivo** |
| Configuração de gatilhos do Google Cloud Build | *Não executa* | **Dono exclusivo** |
| Cadastro e injeção de segredos no Secret Manager | Fornece nomes e valores | **Dono exclusivo** |
| Correção de falhas e pendências apontadas em issues | **Dono** | *Não interfere no código* |

> **Princípio de isolamento:** A infraestrutura nunca altera regras de negócio, lógica de endpoints ou arquivos de código da aplicação. Se um repositório apresentar falha de containerização, segredos expostos ou ausência de documentação, a infraestrutura abre issues no GitHub detalhando o problema e devolve a tarefa para o desenvolvedor resolver.

---

## 2. As 7 etapas do ciclo de vida de um projeto

```text
[1. MVP no Git] ──▶ [2. Documentação C4 + Scan] ──▶ [3. Chamado por E-mail]
                                                             │
[6. Entrega do Resumo] ◀── [5. Provisionamento GCP] ◀── [4. Inspeção Técnica]
          │                                                  │ (se reprovado)
[7. Ciclo Contínuo Git]                                      ▼
                                                   [Issues no GitHub p/ o Dev]
```

### Etapa 1: Concepção e MVP na branch `main`
O desenvolvedor cria o repositório na organização com nome padronizado em kebab-case, desenvolve o MVP funcional, cria o `Dockerfile` e implementa os testes. Todo o código inicial reside exclusivamente na branch `main`. Todos os commits devem ser assinados com SSH ed25519.

### Etapa 2: Documentação com C4 Model e Scan Systems
Antes de solicitar qualquer recurso na nuvem, o desenvolvedor roda as skills oficiais:
1. `/scan-systems` para auditar a base de código e gerar `docs/systems/<projeto>.md` e `docs/SYSTEMS_CATALOG.md`.
2. `/c4-architecture` para mapear a arquitetura em Mermaid em `docs/architecture/`.
3. O desenvolvedor revisa e commita a documentação.

### Etapa 3: Abertura do chamado formal
O desenvolvedor envia o e-mail formal para `raulsilva@suape.pe.gov.br` com o assunto `Provisionamento de ambiente GCP - <repositório>`, preenchendo detalhadamente o questionário de disponibilidade, volume e integrações ([ver modelo de chamado](06-chamado-de-provisionamento.md)).

### Etapa 4: Inspeção técnica da infraestrutura
O responsável pela infraestrutura avalia o repositório:
* **Se faltar documentação ou houver pendências impeditivas** (ex.: ausência de Dockerfile, dependência de Cloudflare/Vercel, segredos commitados, vulnerabilidades altas de segurança): a infraestrutura abre **issues no repositório**, responde o e-mail apontando os apontamentos e o chamado fica suspenso até a correção pelo desenvolvedor.
* **Se o projeto estiver em conformidade:** o chamado é aprovado para provisionamento.

### Etapa 5: Provisionamento e amarração do CI/CD
A infraestrutura executa o setup oficial no GCP:
1. Criação dos serviços Cloud Run para **dev**, **hml** e **prod**, dimensionados com base no perfil de uso informado.
2. Criação das branches **`dev`** e **`hml`** a partir da `main` no GitHub.
3. Criação e amarração dos segredos no Secret Manager.
4. Criação do `cloudbuild.yaml` e configuração dos gatilhos automáticos no Cloud Build para cada branch.

### Etapa 6: Alinhamento técnico e entrega do resumo
A infraestrutura e o desenvolvedor alinham detalhes de esteira (rotinas agendadas, cron jobs, variáveis adicionais). A infraestrutura responde o e-mail formalizando a entrega:
* URLs públicas de cada ambiente.
* Lista de gatilhos ativos no Cloud Build.
* Lista de variáveis e segredos configurados.

### Etapa 7: Operação contínua via Git
O desenvolvedor assume a operação normal do ciclo de vida:
* Novas features nascem a partir de `dev`.
* Deploys ocorrem exclusivamente por Pull Requests (`dev → hml → main`).
* A infraestrutura só volta a intervir em caso de solicitação de novos recursos, ajustes de dimensionamento ou incidentes de plataforma.
