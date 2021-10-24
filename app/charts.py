import boto3
import json
import time

# iniciar cliente redshift
client = boto3.client("redshift-data")

def handler(event, context):
       # input parameters passed from the caller event
    # cluster identifier for the Amazon Redshift cluster
    redshift_cluster_id = 'impacta-dataops-cluster'
    # database name for the Amazon Redshift cluster
    redshift_database = 'dev'
    # database user in the Amazon Redshift cluster with access to execute relevant SQL queries
    redshift_user = 'awsuser'

    try:
        
        sql_uf = "select sum(quantidade), uf from vacinas_dw group by uf"
        # execute the input SQL statement in the specified Amazon Redshift cluster
        res_uf = execute_sql(client, sql_uf, redshift_database, redshift_user, redshift_cluster_id)
        res_uf = extract_data(res_uf)

        sql_vacina = "select sum(quantidade), vacina from vacinas_dw group by vacina"
        # execute the input SQL statement in the specified Amazon Redshift cluster
        res_vacina = execute_sql(client, sql_vacina, redshift_database, redshift_user, redshift_cluster_id)
        res_vacina = extract_data(res_vacina)

        sql_data = "select sum(quantidade), data_aplicacao from vacinas_dw group by data_aplicacao"
        # execute the input SQL statement in the specified Amazon Redshift cluster
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