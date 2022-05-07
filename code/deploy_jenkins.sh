#definir localização do python
PYENV_HOME=$WORKSPACE
# criar e ativar venv do python
python3 -m venv $PYENV_HOME
. $PYENV_HOME/bin/activate
# instalar aws sam cli
pip install aws-sam-cli
# construir e fazer deploy da aplicação
sam build
sam package --region us-east-1 --s3-bucket seu-bucket-de-deploy
sam deploy --stack-name dataops-entrega-vacinas-stack --region us-east-1 --capabilities CAPABILITY_IAM --s3-bucket seu-bucket-de-deploy --no-fail-on-empty-changeset
# copiar aplicação estática para o bucket
aws s3 cp index.html s3://dataops-entrega-nomesobrenome/index.html
