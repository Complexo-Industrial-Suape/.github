# Fluxo de trabalho e deploy

[← Voltar ao catálogo da cartilha](../README.md)

O que vale depois que o ambiente está provisionado.

## Cada branch publica no seu ambiente

| Push ou merge em | Publica em |
|---|---|
| `dev` | dev |
| `hml` | hml (homologação) |
| `main` | **prod (produção)** |

Não existe botão de deploy. Entrou na branch, vai para o ar.

## Fluxo de trabalho

```
feature/minha-tarefa ──PR──▶ dev ──PR──▶ hml ──PR──▶ main
                              │           │           │
                         publica em   publica em  publica em
                            dev          hml         PROD
```

1. Crie sua branch a partir de `dev`: `git checkout dev && git pull && git checkout -b feature/descricao`.
2. Rode os testes na sua máquina antes de abrir o PR.
3. Abra PR para `dev`. O merge publica em dev.
4. Quando estiver pronto para validar, abra PR de `dev` para `hml`.
5. Depois da validação, abra PR de `hml` para `main`. Esse merge publica em produção.

| Prefixo de branch | Uso |
|---|---|
| `feature/` | funcionalidade nova |
| `fix/` | correção pelo fluxo normal |
| `hotfix/` | correção urgente de produção |
| `docs/` | só documentação |

## Regras

1. Não faça push direto em `main`. Ela publica em produção na hora, e a proteção automática ainda não está ativa no GitHub. Por enquanto, essa regra depende de você.
2. Não pule ambiente. O caminho é sempre `dev → hml → main`.
3. Rode os testes antes de subir. O pipeline também roda: se falharem, nada é publicado e o ambiente continua na versão anterior.
4. Segredo fica no Secret Manager. Precisa de um novo? Peça por e-mail.
5. Não faça deploy por fora, com `gcloud run deploy` manual ou upload pelo console. O próximo push sobrescreve o que você fez, e o histórico se perde.
6. Migrations andam junto com o código e rodam antes do deploy. Teste localmente e nunca edite uma migration já aplicada em hml ou prod.
7. Atualize a documentação no mesmo PR quando a arquitetura mudar, entrar um banco novo ou um serviço externo.
8. Todo commit sai assinado com a sua chave SSH e aparece como **Verified**. Veja [Autenticação e assinatura com chave SSH](01-chave-ssh-autenticacao-e-assinatura.md).

## Acompanhar o deploy

Abra o [histórico do Cloud Build](https://console.cloud.google.com/cloud-build/builds;region=southamerica-east1?project=inovacao-491419) e procure o build `<projeto>-<ambiente>`, como `suape-drive-dev`. Ele aparece segundos depois do merge e leva de 3 a 10 minutos. Verde quer dizer que a versão está no ar. Vermelho quer dizer que algo falhou: abra o passo com erro e leia o log. O status também aparece ao lado do commit no GitHub.

## Quando o deploy falha

| Onde falhou | O que fazer |
|---|---|
| Testes (`test`, `pre-flight`, `lint-and-test`) | Rode os testes localmente, corrija e faça novo push |
| `docker build` | Rode `docker build .` localmente |
| Migration | Não tente de novo às cegas. Avise a infraestrutura, porque uma migration com erro pode deixar o banco pela metade |
| `PERMISSION_DENIED` ou `secret not found` | É problema de infraestrutura. Mande o link do build por e-mail |
| Teste final (`smoke`) | O serviço subiu mas não respondeu. Veja os logs no Cloud Run |

## Situações especiais

Commit que mexe só em `docs/` ou em arquivos `.md` não dispara deploy.

Para um hotfix, crie a branch a partir de `main` e abra PR para `main`. Depois, leve a correção de volta com PR de `main` para `hml` e de `hml` para `dev`. Se esquecer, o próximo deploy apaga a correção.

Para voltar uma versão, abra o serviço no [Cloud Run](https://console.cloud.google.com/run?project=inovacao-491419), vá em Revisões, escolha a anterior e mande 100% do tráfego para ela. Isso resolve na hora, mas é temporário: corrija o código ou use `git revert` e siga o fluxo normal.

Variáveis de frontend (`VITE_*`) entram no código durante o build. Para mudar o valor, é preciso um novo deploy. Peça por e-mail.
