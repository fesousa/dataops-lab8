count_nome_vacina = vacinas.groupBy("vacina_nome").count()
count_nome_vacina.show()