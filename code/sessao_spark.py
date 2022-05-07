    # INICIAR SESSÃO SPARK
    spark = SparkSession\
        .builder\
        .appName("SparkETL")\
        .getOrCreate()