# LER ARQUIVOS DO S3 (input_path)
vacinas = spark.read\
               .option("inferSchema", "true")\
               .option("header", "true")\
               .option("sep",";")\
               .csv(input_path)    