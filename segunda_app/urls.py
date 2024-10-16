from django.urls import path
from . import views  # importa todas as views da app

# Aqui devem ficar todas as rotas da app
urlpatterns = [
    path('', views.render_calendar, name='agenda'),
    path('adicionar_compromisso', views.add_commitment, name='adicionar_compromisso'),
    path('get_commitments/', views.get_commitments_by_date, name='get_commitments_by_date'),
    path('editar_compromisso/<int:comp_id>/', views.edit_commitment, name='editar_compromisso'),
    path('delete_commitment/<int:comp_id>/', views.delete_commitment, name='delete_commitment'),  # Nova rota para excluir compromisso
]
