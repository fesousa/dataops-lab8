import boto3
import json

# iniciar cliente redshift
client = boto3.client("redshift-data")

def handler(event, context):
    print(event)

    # input parameters passed from the caller event
    # cluster identifier for the Amazon Redshift cluster
    redshift_cluster_id = 'impacta-dataops-cluster'
    # database name for the Amazon Redshift cluster
    redshift_database = 'dev'
    # database user in the Amazon Redshift cluster with access to execute relevant SQL queries
    redshift_user = 'awsuser'

    try:
        
        sql = "select sum(quantidade), uf from vacinas_dw group by uf"
        # execute the input SQL statement in the specified Amazon Redshift cluster
        res = execute_sql(client, sql, redshift_database, redshift_user, redshift_cluster_id)
        print (res)
    except Exception as e:
        raise

    return {'statusCode': 200, 'body': json.dumps(res)}

def execute_sql(client, sql_text, redshift_database, redshift_user, redshift_cluster_id, with_event=True):
    print("Executing: {}".format(sql_text))
    res = client.execute_statement(Database=redshift_database, DbUser=redshift_user, Sql=sql_text,
                                   ClusterIdentifier=redshift_cluster_id, WithEvent=with_event)
    print(res)
    
    return res