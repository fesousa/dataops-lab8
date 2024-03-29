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


```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'
Description: Aplicação servelerless para entrega do data pipeline.
Resources:
  # Bucket para aplicação estática com JS
  S3BucketEntrega:
    Type: 'AWS::S3::Bucket'
    Properties:
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false
      BucketName: dataops-entrega-nomesobrenome # nome do bucket
      WebsiteConfiguration:
        IndexDocument: index.html # arquivo index da aplicação
  # Política de acesso ao Bucket, para poder acessar de qualquer lugar
  BucketEntregaPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref S3BucketEntrega
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Action:
              - 's3:GetObject'
            Effect: Allow
            Resource: !Join
              - ''
              - - 'arn:aws:s3:::'
                - !Ref S3BucketEntrega  
                - /*
            Principal: '*'
            Sid: 'PublicReadGetObject'
  # API gateway - criação de endpoints de API para acesso aos dados
  ApiGatewayEntrega:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      OpenApiVersion: '2.0'
  # Função lambda para executar o código da API
  LambdaEntrega:
    Type: 'AWS::Serverless::Function'
    Properties:
      FunctionName: dataops-entrega #nome da função
      Handler: charts.handler # nome do arquivo e método de onde está a função
      Runtime: python3.7 # ambiente de execução
      CodeUri: ./app # local onde estarão os arquivos da função
      Description: Dados para criação de gráficos.
      MemorySize: 256 # memória utilizada pela funçãop
      Timeout: 30 # tempo máximo de execução, em segundos
      Role: !Sub arn:aws:iam::${AWS::AccountId}:role/LabRole # IAM role da função para permissões a outros recursos da AWS
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /
            Method: get
            RestApiId:
              Ref: ApiGatewayEntrega
# Saída do CloudFormation - URL do bucket
Outputs:
  WebsiteURL:
    Value: !GetAtt
      - S3BucketEntrega 
      - WebsiteURL
    Description: URL do site no S3
  APIGatewayURL:
    Description: URL das APIs
    Value: !Sub "https://${ApiGatewayEntrega}.execute-api.${AWS::Region}.amazonaws.com/prod/"
```


4. Ainda na pasta `lab8` no VSCode, crie um arquivo `index.html` com o conteúdo a seguir. Este arquivo contém a aplicação estática que será disponibilizada no S3 e consome a API criada com API gateway e Lambda. Ela cria gráficos com ECharts dos dados que estão no Redshift. Devemos trocar o parâmetro `url` do `ajax` para a url do API Gateway que será criada com o template do SAM anterior.

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Vacinação COVID</title>
    <!-- Inclusão do jQuery e ECharts -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.2.1/dist/echarts.min.js"></script>
  </head>
  <body>
    <!-- divs onde serão colocadas os raficos -->
    <div id="uf" style="width: 600px;height:400px;"></div>
    <div id="vacinas" style="width: 600px;height:400px;"></div>
    <div id="datas" style="width: 600px;height:900px;"></div>
    <script type="text/javascript">

      var chartUf = echarts.init(document.getElementById('uf'));
      var chartVacinas = echarts.init(document.getElementById('vacinas'));
      var chartDatas = echarts.init(document.getElementById('datas'));

      // Executar chamada para a API
      var data = $.ajax({
          // trocar pela URL do API ateway
          url: '<SUA URL API GATEWAY>',
          type: 'GET',
          dataType: 'JSON',
          success: function(response) {
              // grafico de UF
              var optionUf = {
                title: {
                  text: 'Vacinas por UF'
                },                
                xAxis: {
                  data: response['uf']['dim']
                },
                yAxis: {},
                series: [
                  {
                    name: 'vacinas',
                    type: 'bar',
                    data: response['uf']['value'],
                    label: {
                      show: true,
                      position: 'top'
                    },
                  }
                ]
              };              
              chartUf.setOption(optionUf);
              
              // gráfico de tipo de vacinas
              data_vacinas = []
              for (var i = 0; i < response['vacina']['dim'].length; i++) {
                data_vacinas.push({
                  name: response['vacina']['dim'][i],
                  value: response['vacina']['value'][i],
                })
              }

              var optionVacina = {
                title: {
                  text: 'Vacinas por tipo'
                },                
                series: [
                  {
                    type: 'treemap',
                    data: data_vacinas,
                    label: {
                      show: true,
                      position: 'insideTopLeft',
                      formatter: function (params) {
                        return (params.name) + `- `+ (params.value);
                      }
                    },
                  }
                ]
              };              
              chartVacinas.setOption(optionVacina);

              // gráfico de datas
              data_datas = []
              for (var i = 0; i < response['data']['dim'].length; i++) {                
                data_datas.push([
                  response['data']['dim'][i],
                  response['data']['value'][i]
                ]);

              }

              var max = (Math.max.apply(Math,response['data']['value']))
              var optionData = {
                tooltip: {
                  position: 'top',
                  formatter: function (p) {
                    var format = echarts.format.formatTime('yyyy-MM-dd', p.data[0]);
                    return format + ': ' + p.data[1];
                  }
                },
                visualMap: {
                  min: 0,
                  max: max,
                  calculable: true,
                  orient: 'vertical',
                  left: '300',
                  top: 'center',
                  inRange: {
                    color: ['#F8F8FF', '#002366']
                  },
                },
                calendar: [
                  {
                    orient: 'vertical',
                    range: '2021',
                    cellSize: [30, 'auto'],
                  }
                ],
                series: [
                  {
                    type: 'heatmap',
                    coordinateSystem: 'calendar',
                    calendarIndex: 0,
                    data: data_datas
                  }
                  
                ]
              };              
              chartDatas.setOption(optionData);
          }
      });      
    </script>
  </body>
</html>
```



5. Ainda na pasta `lab8` no VSCode, crie uma pasta `app`

6. Dentro da pasta `lab8/app` crie o arquivo `charts.py` com o conteúdo a seguir. Este script será a função lambda que lê os dados do Redshift e retorna um JSON com os resultados. Ela será a execução do endpoint do API Gateway. Troque `<ID-CLUSTER-REDSHIFT>` pelo id do seu cluster Redshift criado no [Laboratório 5](https://github.com/fesousa/dataops-lab5).

```py
import boto3
import json
import time

# iniciar cliente redshift
client = boto3.client("redshift-data")

def handler(event, context):
    # Nome do cluster redshift
    redshift_cluster_id = '<ID-CLUSTER-REDSHIFT>'
    # nome do database redshift
    redshift_database = 'dev'
    # nome do usuário do database redshift
    redshift_user = 'awsuser'

    try:
        # executar consulta no redshift para retornar quantidade de vacinas por UF
        sql_uf = "select sum(quantidade), uf from vacinas_dw group by uf"
        res_uf = execute_sql(client, sql_uf, redshift_database, redshift_user, redshift_cluster_id)
        res_uf = extract_data(res_uf)

        # executar consulta no redshift para retornar quantidade de vacinas por nome
        sql_vacina = "select sum(quantidade), vacina from vacinas_dw group by vacina"
        res_vacina = execute_sql(client, sql_vacina, redshift_database, redshift_user, redshift_cluster_id)
        res_vacina = extract_data(res_vacina)

        # executar consulta no redshift para retornar quantidade de vacinas por data de aplicacão
        sql_data = "select sum(quantidade), data_aplicacao from vacinas_dw group by data_aplicacao"
        res_data = execute_sql(client, sql_data, redshift_database, redshift_user, redshift_cluster_id)
        res_data = extract_data(res_data)

    except Exception as e:
        raise

    return {'statusCode': 200, "body":json.dumps({"uf":res_uf, "vacina":res_vacina, "data":res_data}), "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET"}}

def execute_sql(client, sql_text, redshift_database, redshift_user, redshift_cluster_id, with_event=True):
    print("Executing: {}".format(sql_text))
    res = client.execute_statement(Database=redshift_database, DbUser=redshift_user, Sql=sql_text,
                                   ClusterIdentifier=redshift_cluster_id, WithEvent=with_event)
    q_id = res['Id']
    # esperar resultado
    for i in range(1, 10):
        res = client.describe_statement(Id=q_id)
        if res['Status'] == 'FINISHED':
            break
        time.sleep(0.1)
    res = client.get_statement_result(Id=q_id)

    return res['Records']

def extract_data(res):
    dim = []
    value = []
    print(res)
    for r in res:
        dim.append(r[1]['stringValue'])
        value.append(r[0]['longValue'] )
    return {'dim': dim, 'value': value}
```

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
    
Last update: 2023-11-11 01:37:48
</div>