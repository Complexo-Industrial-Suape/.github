# Brief para subagente por parte publicável

Copie o bloco, troque `<PARTE>` e `<PASTA>`, e cole `references/gcp-readiness-checks.md` inteiro onde indicado (o subagente não tem os arquivos desta skill). Dispare todos os subagentes na mesma mensagem.

```text
Você está varrendo a parte publicável <PARTE>, na pasta <PASTA> deste repositório, para o relatório que a infraestrutura da CTIC de Suape usa para provisionar Cloud Run, Cloud SQL e Secret Manager. Somente leitura: não altere nenhum arquivo e não grave em docs/. Quem escreve o relatório é o agente principal.

Escopo: só <PASTA> e os arquivos da raiz que afetam esta parte (docker-compose, .env.example, CI, lockfile da raiz). Pacotes compartilhados importados por esta parte entram.

Para cada item abaixo, traga evidência como caminho relativo à raiz do repositório e linha (ex.: api/src/main.py:42). Sem evidência, escreva "nenhum encontrado" e a busca que fez. Se uma ferramenta não existir (pip-audit, npm, docker, rede), escreva "não verificado: <motivo>"; nunca afirme o que não executou.

1. Veredito de cada item aplicável das seções 3.1 e 3.2 da cartilha (atendido, pendente, não se aplica, não verificado), incluindo detecção de outro provedor de nuvem e de suape-brand.
2. Publicação: Dockerfile, imagem base, porta e se lê PORT, comando de start, rota de health, USER do container.
3. Variáveis de ambiente: nome, arquivo:linha onde é lida, build ou runtime (VITE_*, NEXT_PUBLIC_*, REACT_APP_*, PUBLIC_* são build), se é segredo. NUNCA escreva valores, nem parciais.
4. Dados: banco e driver, migrations (ferramenta, pasta, como e quando rodam), armazenamento de arquivos, escrita em disco local.
5. Tarefas agendadas e integrações externas (APIs, e-mail, SMS, Google, IA).
6. Rotas: até ~30, uma linha cada (método, caminho, auth, arquivo:linha). Acima disso, agrupe por prefixo ou blueprint (métodos, prefixo, contagem, auth, arquivo) e liste uma a uma só as rotas sem auth e as chamadas por sistema externo.
7. Testes: comando, número de arquivos de teste, cobertura se houver relatório.
8. Segurança: execute as verificações de segredos e de dependências do ecossistema (padrões em scanning-for-hardcoded-secrets e auditing-python-dependencies ou auditing-npm-dependencies; abra a skill só se precisar de um padrão que não está na referência abaixo). CVE com pip-audit (fallbacks uv e pipx) e npm audit --omit=dev: pacote, versão, severidade, ID, versão corrigida. Alta/crítica bloqueia; média/baixa não.
9. Variáveis lidas nesta parte que não aparecem em .env.example nem no README (cada uma bloqueia, por documentação incompleta).
10. Pendências: uma linha por problema, no imperativo, com arquivo, ação e se bloqueia (só os seis casos: CVE alta/crítica ou a confirmar; outro provedor; segredo commitado; parte sem Dockerfile; segredo com padrão inseguro; documentação obrigatória ausente ou incompleta).

Referência de verificações:
<cole aqui references/gcp-readiness-checks.md>

Devolva texto com os títulos 1 a 10, tabelas onde couber, sem introdução nem conclusão.
```

Ao receber os resultados, confira dois ou três `arquivo:linha` de cada subagente antes de copiar. Se um subagente afirmar "atendido" sem evidência, trate como `não verificado` ou verifique você.
