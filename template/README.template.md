# DataOps - Laboratório 8

Entrega e Visualização

As instruções do laboratório estão em português. Para alterar o idioma, procure a opção na barra inferior do console AWS.


## Objetivos

* Disponibilizar uma API para retornar dados do Redshift
* Disponibilizar uma aplicação estática no S3 para consumir a API e mostrar gráficos



## Entrega com API Gateway, Lambda e Visualização com S3 e ECharts

1. Inicie o cluster Redshift criado no [Laboratório 5](https://github.com/fesousa/dataops-lab5)

2. Abra o VSCode e crie uma pasta para este laboratório (`lab8`)

3. Na pasta `lab8` crie um arquivo `template.yaml` com o conteúdo do código abaixo. Troque `nomesobrenome` no nome do bucket (`dataops-entrega-nomesobrenome`) pelo seu nome e sobrenome.

https://github.com/fesousa/dataops-lab8/blob/99ec56348890d15dccea5b884eb790bb64316263/template.yaml#L1-L66

4. Ainda na pasta `lab8` no VSCode, crie um arquivo `index.html` com o conteúdo a seguir. Este arquivo contém a aplicação estática que será disponibilizada no S3 e consome a API criada com API gateway e Lambda. Ela cria gráficos com ECharts dos dados que estão no Redshift. Devemos trocar o parâmetro `url` do `ajax` para a url do API Gateway que será criada com o template do SAM anterior.

https://github.com/fesousa/dataops-lab8/blob/99ec56348890d15dccea5b884eb790bb64316263/index.html#L1-L132

5. Ainda na pasta `lab8` no VSCode, crie uma pasta `app`

6. Dentro da pasta `lab8/app` crie o arquivo `charts.py` com o conteúdo a seguir. Este script será a função lambda que lê os dados do Redshift e retorna um JSON com os resultados. Ela será a execução do endpoint do API Gateway. Troque `<ID-CLUSTER-REDSHIFT>` pelo id do seu cluster Redshift criado no [Laboratório 5](https://github.com/fesousa/dataops-lab5).


https://github.com/fesousa/dataops-lab8/blob/99ec56348890d15dccea5b884eb790bb64316263/app/charts.py#L1-L61


7. Crie um novo repositório `dataops-lab8` no seu Github e envie os arquivos da pasta `lab8`

8.	Crie um novo projeto no Jenkins

    8.1. Acesse o Jenkins no EC2 do seu ambiente

    8.2. Na página inicial, clique em <img src="images/Imagem14.png" height='25'/>

    8.3. Na página de criação de um novo item, coloque as seguintes configurações:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a. Enter an item name: DataOpsDeployEntrega

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;b. Copy from : DataOpsDeployColeta (criado no [Laboratório 4](https://github.com/fesousa/dataops-lab4))

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Criaremos um novo item no Jenkins parecido com DataOpsDeployColeta

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c. Clique em <img src="images/Imagem16.png" height='25'/>

&nbsp;&nbsp;&nbsp;&nbsp;8.4. Na configuração do item, altere o seguinte:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a. Provider: DeployEntregaProvider

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;b.	Na seção <img src="images/Imagem17.png" height='25'/> altere os comandos que serão executados para o seguinte:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;https://github.com/fesousa/dataops-lab8/blob/c446d10a237967a55ee0cc84bfa5fbae7d8bb882/code/deploy_jenkins.sh#L1-L13


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lembre-se de alterar `seu-bucket-de-deploy` pelo seu bucket de deploy criado no [Laboratório 7](https://github.com/fesousa/dataops-lab7) e `dataops-entrega-nomesobrenome` pelo nome do bucket criado no template deste laboratório

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c. Clique em <img src="images/Imagem18.png" height='25'/>


9.	Crie um pipeline de entrega no CodePipeline com as seguintes características:

    9.1. Nome do pipeline: dataops-entrega-pipeline

    9.2. Escolha a função de execução LabRole

    9.3. Provedor de origem: repositório dataops-lab8 do seu Github (lembre-se de escolher a branch correta)

    9.4. Etapa de compilação: 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a. Jenkins

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;b.	Nome do Provedor: DeployEntregaProvider

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c. URL do servidor: IP e porta onde está seu Jenkins

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d. Nome do Projeto: DataOpsDeployEntrega

&nbsp;&nbsp;&nbsp;&nbsp;9.5. Sem etapa de implantação

10.	Verifique se o pipeline executou sem problemas

11.	No console da AWS, procure pelo serviço CloudFormation

12.	Abra a pilha `dataops-entrega-vacinas-stack`

13.	Clique na aba <img src="images/Imagem19.png" height='25'/>

14.	Copie o valor da chave `APIGatewayURL`. Ela será uma URL parecida com a seguinte: `https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/`. 

<img src="images/Imagem20.png" width='100%'/>

15.	Cole a URL na barra de endereço do navegador e verifique se obtém um resultado parecido com o seguinte. Essa é a URL onde está sendo executada a API de consulta aos dados do Redshift. Ao abri-la, a função lambda é executada, as consultas são realizadas no Redshift e os dados são retornados no formato JSON.

<img src="images/Imagem21.png" height='500'/>

16.	Volte ao VSCode no arquivo `index.html` criado no começo do lab e cole essa mesma URL no parâmetro url da chamada `ajax`. Depois, envie a alteração para o repositório do Github.

<img src="images/Imagem25.png" height='200'/>

17.	Espere o pipeline executar e verifique se tudo correu sem problemas

18.	Volte ao CloudFormation, na mesma pilha aberta anteriormente (`dataops-entrega-vacinas-stack`), na aba `Saídas`, copie o valor da chave `WebsiteURL`. Ela será uma URL parecida com a seguinte: `http://dataops-entrega-nomesobrenome.s3-website-us-east-1.amazonaws.com`. Cole essa URL no navegador e veja o resultado. Você deve ver 3 gráficos.


<table>
<tr>
<td><img src="images/Imagem22.png" height='300'/></td>
<td rowspan='2'><img src="images/Imagem24.png" height='800'/></td>
</tr>
<tr>
<td><img src="images/Imagem23.png" height='300'/></td>
</tr>
</table>







## Finalização do Laboratório

Termine o cluster do EMR para economizar recursos da sua conta.


<div class="footer">
    &copy; 2022 Fernando Sousa
    <br/>
    {{update}}
</div>