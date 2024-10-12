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
    # Captura a data selecionada do calendário
    date_str = request.GET.get('date')  # A data vem como um parâmetro GET do calendário

    if request.method == 'POST':
        try:
            # Converte a data de 'd/m/Y' para o formato esperado pelo Django 'Y-m-d'
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')  # Exemplo: '28/09/2024'
            
            # Combina a data com a hora de início e fim para gerar os datetime completos
            start_time = datetime.combine(date_obj, datetime.strptime(request.POST['hora_inicio'], '%H:%M').time())
            
            # Verifica se a hora de fim foi passada, caso contrário, use 23:59 como padrão
            end_time = datetime.combine(date_obj, datetime.strptime(request.POST.get('hora_fim', '23:59'), '%H:%M').time())
            
            # Torna as datas timezone-aware para evitar os warnings de naive datetime
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

    # Passa a data selecionada para o template de adição de compromisso
    return render(request, "segunda_app/add_commitment_page.html", {'selected_date': date_str})

def get_commitments_by_date(request):
    # Captura a data da requisição GET
    date_str = request.GET.get('date')

    # Verifica se a data foi fornecida
    if not date_str:
        return JsonResponse({'error': 'Data não fornecida'}, status=400)
    
    try:
        # Tenta converter a data no formato esperado 'd/m/Y' (ex: 23/10/2024)
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        return JsonResponse({'error': 'Formato de data inválido'}, status=400)
    
    # Filtra os compromissos para a data informada
    compromissos = Commitment.objects.filter(time_start__date=date_obj)

    # Prepara os dados para retorno
    compromissos_data = [
        {
            'processo': comp.processes,
            'local': comp.location,
            'observacoes': comp.description,
            'hora_inicio': comp.time_start.strftime('%H:%M'),
            'hora_fim': comp.time_end.strftime('%H:%M')
        } for comp in compromissos
    ]
    
    # Retorna os dados dos compromissos em formato JSON
    return JsonResponse({'compromissos': compromissos_data})
