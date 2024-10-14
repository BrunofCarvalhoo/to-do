from django.shortcuts import render, redirect
from datetime import datetime
from django.utils import timezone
from .models import Commitment
import json
from django.http import JsonResponse

def render_calendar(request):
    # Obtenha todas as datas dos compromissos
    compromissos = Commitment.objects.values_list('time_start', flat=True)
    
    # Converta para uma lista de strings no formato "YYYY-MM-DD"
    datas_com_compromissos = [comp.date().isoformat() for comp in compromissos]
    
    context = {
        'datas_com_compromissos': json.dumps(datas_com_compromissos)  # Passa como JSON
    }
    return render(request, "segunda_app/calendar_page.html", context)

def add_commitment(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')  # Obtém a data do POST
        try:
            # Converte a data de 'd/m/Y' para um objeto datetime
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')

            # Combina a data com a hora de início e fim
            start_time = datetime.combine(date_obj, datetime.strptime(request.POST['hora_inicio'], '%H:%M').time())
            end_time = datetime.combine(date_obj, datetime.strptime(request.POST['hora_fim'], '%H:%M').time())

            # Torna as datas timezone-aware
            start_time = timezone.make_aware(start_time)
            end_time = timezone.make_aware(end_time)

            # Cria o compromisso no banco de dados
            Commitment.objects.create(
                time_start=start_time,
                time_end=end_time,
                processes=request.POST['processo'],
                location=request.POST['local'],
                description=request.POST['observacoes']
            )
            return redirect('agenda')  # Redireciona para a agenda após salvar o compromisso
        except ValueError:
            # Caso a data ou hora esteja em um formato inválido, retorna uma mensagem de erro
            return render(request, "segunda_app/add_commitment_page.html", {
                'selected_date': date_str,
                'error': 'Formato de data ou hora inválido. Tente novamente.'
            })
    else:
        # Captura a data selecionada do calendário via GET
        date_str = request.GET.get('date')
        return render(request, "segunda_app/add_commitment_page.html", {'selected_date': date_str})

def get_commitments_by_date(request):
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': 'Data não fornecida'}, status=400)
    
    try:
        # Formata a data corretamente de acordo com o que está vindo do JavaScript ('YYYY-MM-DD')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return JsonResponse({'error': 'Formato de data inválido'}, status=400)
    
    # Carrega todos os compromissos para a data específica e os ordena pelo horário de início
    compromissos = Commitment.objects.filter(time_start__date=date_obj).order_by('time_start')

    # Prepara os dados dos compromissos em uma lista
    compromissos_data = [
        {
            'processo': comp.processes,
            'local': comp.location,
            'observacoes': comp.description,
            'hora_inicio': comp.time_start.strftime('%H:%M'),
            'hora_fim': comp.time_end.strftime('%H:%M')
        } for comp in compromissos
    ]
    
    # Retorna os dados como JSON
    return JsonResponse({'compromissos': compromissos_data})
