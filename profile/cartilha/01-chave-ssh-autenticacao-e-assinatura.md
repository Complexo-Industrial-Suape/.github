# Autenticação e assinatura com chave SSH

[← Voltar ao catálogo da cartilha](../README.md)

**Obrigatório para todo desenvolvedor.** Você usa chaves SSH para duas coisas: entrar no GitHub (`git clone`, `git push`) e assinar cada commit que faz. O GitHub marca o commit assinado com o selo **Verified**. Sem o selo, ninguém consegue afirmar que o commit é seu.

## Por que isso é obrigatório

- **Autoria comprovada.** Nome e e-mail do commit são texto livre: qualquer pessoa pode commitar como você. A assinatura prova que a chave foi usada.
- **Código de produção.** Um merge na `main` publica em produção na hora. Precisamos saber de quem veio cada alteração.
- **Sem senha nem token.** A chave SSH substitui senha e token de acesso na linha de comando.

## Antes de começar

- Conta no GitHub, membro da org [Complexo-Industrial-Suape](https://github.com/Complexo-Industrial-Suape).
- Seu **e-mail institucional (@suape.pe.gov.br) adicionado e verificado** em [Settings → Emails](https://github.com/settings/emails). O selo Verified só aparece se o e-mail do commit for um e-mail verificado da sua conta.
- `git` e `ssh` instalados. No Windows, use o WSL ou o Git Bash. Os comandos abaixo são os mesmos.
- Opcional, para cadastrar as chaves pelo terminal: a [GitHub CLI](https://cli.github.com) (`gh`).

## 1. Gerar as chaves

Crie **duas** chaves, uma para autenticar e outra para assinar. Assim você revoga uma sem perder a outra.

```bash
ssh-keygen -t ed25519 -a 100 -C "seu.email@suape.pe.gov.br (github auth, $(hostname))" -f ~/.ssh/id_ed25519_github
ssh-keygen -t ed25519 -a 100 -C "seu.email@suape.pe.gov.br (github signing, $(hostname))" -f ~/.ssh/id_ed25519_github_signing
```

- Use o tipo **ed25519**. Não gere RSA nem DSA.
- **Defina uma senha (passphrase)** quando o comando pedir. Sem ela, quem copiar o arquivo da chave usa a sua identidade.
- Carregue as chaves no agente, para digitar a senha uma vez por sessão:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_github ~/.ssh/id_ed25519_github_signing
```

Cada arquivo gera um par: o sem extensão é a chave **privada** (secreta) e o `.pub` é a chave **pública** (a que você cadastra no GitHub).

## 2. Dizer ao SSH qual chave usar

Acrescente ao arquivo `~/.ssh/config` (crie se não existir) e proteja-o:

```text
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```

```bash
chmod 600 ~/.ssh/config ~/.ssh/id_ed25519_github ~/.ssh/id_ed25519_github_signing
```

## 3. Configurar o git para assinar

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@suape.pe.gov.br"
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519_github_signing.pub
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# permite conferir assinaturas localmente (git log --show-signature)
echo "seu.email@suape.pe.gov.br namespaces=\"git\" $(cut -d' ' -f1,2 ~/.ssh/id_ed25519_github_signing.pub)" > ~/.ssh/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
```

Com `commit.gpgsign=true`, todo commit e tag sai assinado sem você fazer nada. O `user.email` precisa ser o e-mail verificado do passo anterior.

## 4. Cadastrar as chaves no GitHub

O GitHub trata chave de autenticação e chave de assinatura separadamente. Cadastre as duas, cada uma com o seu tipo.

**Pelo terminal:**

```bash
gh auth refresh -h github.com -s admin:public_key,admin:ssh_signing_key
gh ssh-key add ~/.ssh/id_ed25519_github.pub --title "$(hostname) (auth)" --type authentication
gh ssh-key add ~/.ssh/id_ed25519_github_signing.pub --title "$(hostname) (signing)" --type signing
```

**Pelo site:** em [Settings → SSH and GPG keys → New SSH key](https://github.com/settings/ssh/new), cole o conteúdo de cada arquivo `.pub` (`cat ~/.ssh/id_ed25519_github.pub`) e escolha o tipo: **Authentication Key** para a primeira e **Signing Key** para a segunda.

Cole sempre o arquivo `.pub`. Nunca cole nem envie o arquivo sem extensão.

## 5. Testar

```bash
ssh -T git@github.com
```

Na primeira vez, o SSH pergunta se confia no servidor. Confira se a impressão digital mostrada é uma das publicadas pelo GitHub em [GitHub's SSH key fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints) (a ED25519 é `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`) e só então responda `yes`. A resposta esperada é `Hi <seu-usuário>! You've successfully authenticated...`.

Teste a assinatura em um repositório seu:

```bash
git commit --allow-empty -m "teste: commit assinado"
git log --show-signature -1     # deve mostrar: Good "git" signature
git push
```

No GitHub, o commit precisa aparecer com o selo **Verified**. Se aparecer **Unverified** ou sem selo, veja a tabela de problemas abaixo.

## 6. Repositórios que você já clonou

Clones feitos por HTTPS continuam pedindo senha ou token. Troque o endereço para SSH:

```bash
git remote set-url origin git@github.com:Complexo-Industrial-Suape/<repositório>.git
```

Para que os próximos clones já usem SSH: `gh config set git_protocol ssh -h github.com`.

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Commit aparece **Unverified** ou sem selo | A chave de assinatura não está cadastrada como **Signing Key** | Cadastre de novo escolhendo o tipo certo (passo 4) |
| Commit **Unverified**, com a chave cadastrada | O e-mail do commit não é um e-mail verificado da sua conta | Confira `git config user.email` e [Settings → Emails](https://github.com/settings/emails) |
| Commit sem assinatura nenhuma | `commit.gpgsign` não está ligado, ou o commit veio de outra máquina | `git config --global commit.gpgsign true`. Para corrigir um commit já feito, veja abaixo |
| `error: Load key ... bad permissions` | Chave privada legível por outros usuários | `chmod 600 ~/.ssh/id_ed25519_github*` |
| `Permission denied (publickey)` | Chave de autenticação não cadastrada, ou não carregada no agente | Rode `ssh-add -l` e confira o passo 4 |
| `Could not open a connection to your authentication agent` | O `ssh-agent` não está rodando nesta sessão | `eval "$(ssh-agent -s)"` e depois `ssh-add` |
| `error: Signing failed` ou `incorrect passphrase` | A chave de assinatura não está carregada no agente | `ssh-add ~/.ssh/id_ed25519_github_signing` |
| `Permission denied` só no WSL ou só no Windows | WSL e Windows têm `~/.ssh` separados | Gere e cadastre chaves em cada ambiente em que você commita |

Para assinar um commit que você já fez e ainda não publicou: `git commit --amend --no-edit -S`. Para vários commits, `git rebase --exec 'git commit --amend --no-edit -n -S' -i <base>`.

## Regras de segurança

1. **A chave privada é só sua.** Não commite, não mande por e-mail ou chat, não copie para pasta compartilhada.
2. **Uma chave por máquina.** Cada computador seu tem o próprio par. Não copie a privada de um para outro.
3. **Perdeu a máquina, ou suspeita de vazamento?** Remova as chaves em [Settings → SSH and GPG keys](https://github.com/settings/keys), gere um par novo e avise a infraestrutura por e-mail.
4. **Troca de computador.** Gere chaves novas e cadastre. Depois remova as antigas do GitHub.
5. Bots e automações usam credencial própria combinada com a infraestrutura. Nunca a sua chave pessoal.

## Como a CTIC confere

O critério é o selo **Verified** no GitHub, em todos os commits que você publica. Com o plano atual do GitHub nas orgs, o GitHub **não bloqueia** automaticamente um push de commit sem assinatura. Por isso a verificação é manual, na revisão do PR e na inspeção do chamado de provisionamento. Commit sem o selo é devolvido para você assinar de novo.
