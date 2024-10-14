from django.shortcuts import render, redirect
from datetime import datetime
from django.utils import timezone
from .models import Commitment
import json
from django.http import JsonResponse
import pytz

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
        date_str = request.POST.get('date')
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            start_time = datetime.combine(date_obj, datetime.strptime(request.POST['hora_inicio'], '%H:%M').time())
            end_time = datetime.combine(date_obj, datetime.strptime(request.POST['hora_fim'], '%H:%M').time())
            
            tz = pytz.timezone('America/Sao_Paulo')
            start_time = timezone.make_aware(start_time, timezone=tz)
            end_time = timezone.make_aware(end_time, timezone=tz)

            Commitment.objects.create(
                time_start=start_time,
                time_end=end_time,
                processes=request.POST['processo'],
                location=request.POST['local'],
                description=request.POST['observacoes']
            )
            return redirect('agenda')
        except ValueError:
            return render(request, "segunda_app/add_commitment_page.html", {
                'selected_date': date_str,
                'error': 'Formato de data ou hora inválido. Tente novamente.'
            })
    else:
        date_str = request.GET.get('date')
        return render(request, "segunda_app/add_commitment_page.html", {'selected_date': date_str})

def get_commitments_by_date(request):
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': 'Data não fornecida'}, status=400)
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato de data inválido'}, status=400)
    
    compromissos = Commitment.objects.filter(time_start__date=date_obj).order_by('time_start')

    compromissos_data = [
        {
            'processo': comp.processes,
            'local': comp.location,
            'observacoes': comp.description,
            'hora_inicio': timezone.localtime(comp.time_start).strftime('%H:%M'),
            'hora_fim': timezone.localtime(comp.time_end).strftime('%H:%M')
        } for comp in compromissos
    ]
    
    return JsonResponse({'compromissos': compromissos_data})
