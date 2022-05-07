# instalar bibliotecas
sc.install_pypi_package("pandas==0.25.1") 
sc.install_pypi_package("matplotlib")

count_nome_vacina_pd = count_nome_vacina.toPandas() # transformar em Pandas

import matplotlib.pyplot as plt
plt.clf() #limpar gráficos da memória
fig, ax = plt.subplots(figsize=(8,5))
w,a,b = ax.pie(count_nome_vacina['count'], labels=count_nome_vacina['vacina_nome'], autopct='%1.1f%%')
plt.title('Distribuicao por nome de vacina')
# visualizar gráfico
%matplot plt