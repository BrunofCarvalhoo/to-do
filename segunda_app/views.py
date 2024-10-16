from django.shortcuts import render, redirect
from datetime import datetime
from django.utils import timezone
from .models import Commitment
import json
from django.http import JsonResponse, HttpResponseBadRequest
import pytz
from django.urls import reverse

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
                'error': 'Formato de data ou hora inválido. Tente novamente.',
                'form_action': reverse('adicionar_compromisso'),
                # Preenche os campos com os dados submetidos para não perder as informações
                'hora_inicio': request.POST.get('hora_inicio'),
                'hora_fim': request.POST.get('hora_fim'),
                'processo': request.POST.get('processo'),
                'local': request.POST.get('local'),
                'observacoes': request.POST.get('observacoes')
            })
    else:
        date_str = request.GET.get('date')
        return render(request, "segunda_app/add_commitment_page.html", {
            'selected_date': date_str,
            'form_action': reverse('adicionar_compromisso')
        })

def edit_commitment(request, comp_id):
    try:
        commitment = Commitment.objects.get(id=comp_id)
    except Commitment.DoesNotExist:
        return render(request, 'segunda_app/add_commitment_page.html', {
            'error': 'Compromisso não encontrado.'
        })

    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            start_time = datetime.combine(date_obj, datetime.strptime(request.POST['hora_inicio'], '%H:%M').time())
            end_time = datetime.combine(date_obj, datetime.strptime(request.POST['hora_fim'], '%H:%M').time())

            tz = pytz.timezone('America/Sao_Paulo')
            start_time = timezone.make_aware(start_time, timezone=tz)
            end_time = timezone.make_aware(end_time, timezone=tz)

            # Atualiza os campos do compromisso
            commitment.time_start = start_time
            commitment.time_end = end_time
            commitment.processes = request.POST['processo']
            commitment.location = request.POST['local']
            commitment.description = request.POST['observacoes']
            commitment.save()
            return redirect('agenda')
        except ValueError:
            return render(request, "segunda_app/add_commitment_page.html", {
                'selected_date': date_str,
                'commitment': commitment,
                'error': 'Formato de data ou hora inválido. Tente novamente.',
                'form_action': reverse('editar_compromisso', args=[comp_id]),
                # Preenche os campos com os dados submetidos para não perder as informações
                'hora_inicio': request.POST.get('hora_inicio'),
                'hora_fim': request.POST.get('hora_fim'),
                'processo': request.POST.get('processo'),
                'local': request.POST.get('local'),
                'observacoes': request.POST.get('observacoes')
            })
    else:
        # Preenche o formulário com os dados existentes
        selected_date = commitment.time_start.strftime('%d/%m/%Y')
        context = {
            'selected_date': selected_date,
            'hora_inicio': commitment.time_start.strftime('%H:%M'),
            'hora_fim': commitment.time_end.strftime('%H:%M'),
            'processo': commitment.processes,
            'local': commitment.location,
            'observacoes': commitment.description,
            'form_action': reverse('editar_compromisso', args=[comp_id]),
            'commitment': commitment
        }
        return render(request, "segunda_app/add_commitment_page.html", context)

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
            'hora_fim': timezone.localtime(comp.time_end).strftime('%H:%M'),
            'id': comp.id  # Adiciona o ID do compromisso
        } for comp in compromissos
    ]
    
    return JsonResponse({'compromissos': compromissos_data})

def delete_commitment(request, comp_id):
    if request.method == 'DELETE':
        try:
            # Obtém o compromisso a ser excluído
            commitment = Commitment.objects.get(id=comp_id)
            commitment.delete()  # Deleta o compromisso
            return JsonResponse({'success': True}, status=204)  # Retorna sucesso
        except Commitment.DoesNotExist:
            return JsonResponse({'error': 'Compromisso não encontrado'}, status=404)
    else:
        return HttpResponseBadRequest('Método não permitido')
