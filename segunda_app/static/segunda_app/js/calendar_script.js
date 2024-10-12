document.addEventListener("DOMContentLoaded", function() {
    // Verifica se a variável 'datasComCompromissos' foi carregada corretamente
    if (typeof datasComCompromissos === 'undefined') {
        console.error("A variável 'datasComCompromissos' não foi definida.");
        return;
    }

    // Configura o calendário flatpickr
    flatpickr("#datepicker", {
        locale: "pt",              // Idioma para português
        dateFormat: "d/m/Y",       // Formato da data
        inline: true,              // Exibe o calendário inline (não em modal)
        defaultDate: "today",      // Data padrão (hoje)
        firstDayOfWeek: 1,         // Começa a semana na segunda-feira
        onDayCreate: function(dObj, dStr, fp, dayElem) {
            // Formata a data do elemento de dia (ano-mês-dia)
            var dateStr = dayElem.dateObj.toISOString().split('T')[0];  // 'YYYY-MM-DD'

            // Verifica se existe evento para este dia
            if (datasComCompromissos.includes(dateStr)) {
                var eventMarker = document.createElement('div');
                eventMarker.className = 'event-marker';  // Classe do marcador de evento
                dayElem.appendChild(eventMarker);

                // Adiciona um listener de clique no marcador de evento
                eventMarker.addEventListener("click", function() {
                    // Chama a API para carregar compromissos do banco de dados
                    fetch(`/agenda/get_commitments/?date=${dateStr}`)
                        .then(response => response.json())
                        .then(data => {
                            const commitmentsDiv = document.querySelector("#commitments");
                            commitmentsDiv.innerHTML = '';  // Limpa a div de compromissos

                            // Verifica se existem compromissos para o dia
                            if (data.compromissos && data.compromissos.length > 0) {
                                data.compromissos.forEach(comp => {
                                    // Cria um item para cada compromisso
                                    const commitmentItem = document.createElement("div");
                                    commitmentItem.className = 'commitment-item';  // Adiciona uma classe para estilizar
                                    commitmentItem.innerHTML = `
                                        <strong>${comp.processo}</strong><br>
                                        <span>Local: ${comp.local}</span><br>
                                        <span>Início: ${comp.hora_inicio}</span><br>
                                        <span>Fim: ${comp.hora_fim}</span><br>
                                        <p>${comp.observacoes}</p>
                                    `;
                                    commitmentsDiv.appendChild(commitmentItem);
                                });
                            } else {
                                commitmentsDiv.innerHTML = '<p>Nenhum evento para esse dia.</p>';
                            }
                        })
                        .catch(error => {
                            console.error('Erro ao carregar compromissos:', error);
                            // Caso haja erro na requisição, exibe a mensagem de erro
                            const commitmentsDiv = document.querySelector("#commitments");
                            commitmentsDiv.innerHTML = '<p>Ocorreu um erro ao carregar os compromissos.</p>';
                        });
                });
            }
        },
        onChange: function(selectedDates, dateStr, instance) {
            // Lógica adicional para quando o usuário mudar a data no calendário
            // No momento, não precisa de ações adicionais
        }
    });
});
