# Deve-se criar este arquivo!
from django.urls import path
from . import views  # importa todas as views da app

# Aqui devem ficar todas as rotas da app
urlpatterns = [
    path('', views.render_calendar, name='agenda'),                                    # agenda = http://127.0.0.1:8000/agenda/
    path('adicionar_compromisso', views.add_commitment, name='adicionar_compromisso'),# adicionar_compromisso = http://127.0.0.1:8000/agenda/adicionar_compromisso
    path('get_commitments/', views.get_commitments_by_date, name='get_commitments_by_date'),  
]
