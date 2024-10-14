document.addEventListener("DOMContentLoaded", function() {
    const commitmentsDiv = document.querySelector("#commitments");

    // Função para carregar compromissos de um dia específico
    function loadCommitments(dateStr) {
        fetch(`/agenda/get_commitments/?date=${dateStr}`)
            .then(response => response.json())
            .then(data => {
                commitmentsDiv.innerHTML = '';  // Limpa a div de compromissos

                // Verifica se existem compromissos para o dia
                if (data.compromissos && data.compromissos.length > 0) {
                    data.compromissos.forEach(comp => {
                        // Cria um item para cada compromisso
                        const commitmentItem = document.createElement("div");
                        commitmentItem.className = 'commitment-item';  // Classe para estilizar
                        commitmentItem.innerHTML = `
                            <strong>${comp.processo}</strong><br>
                            <span>Local: ${comp.local}</span><br>
                            <span>Início: ${comp.hora_inicio}</span><br>
                            <span>Fim: ${comp.hora_fim}</span><br>
                            <p>${comp.observacoes}</p>
                        `;
                        commitmentsDiv.appendChild(commitmentItem);
                    });

                    // Ajuste para rolagem infinita no container
                    commitmentsDiv.style.overflowY = 'auto';  // Garante a rolagem vertical
                } else {
                    commitmentsDiv.innerHTML = '<p>Nenhum evento para esse dia.</p>';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar compromissos:', error);
                commitmentsDiv.innerHTML = '<p>Ocorreu um erro ao carregar os compromissos.</p>';
            });
    }

    // Configura o calendário flatpickr
    flatpickr("#datepicker", {
        locale: "pt",              // Idioma para português
        dateFormat: "d/m/Y",       // Formato da data
        inline: true,              // Exibe o calendário inline (não em modal)
        defaultDate: "today",      // Data padrão (hoje)
        firstDayOfWeek: 1,         // Começa a semana na segunda-feira
        onDayCreate: function(dObj, dStr, fp, dayElem) {
            var dateStr = dayElem.dateObj.toISOString().split('T')[0];  // 'YYYY-MM-DD'

            if (datasComCompromissos.includes(dateStr)) {
                var eventMarker = document.createElement('div');
                eventMarker.className = 'event-marker';  // Classe do marcador de evento
                dayElem.appendChild(eventMarker);
            }

            // Adiciona o listener de clique no próprio dia
            dayElem.addEventListener("click", function() {
                loadCommitments(dateStr);  // Carrega compromissos quando o dia é clicado
            });
        }
    });
});
