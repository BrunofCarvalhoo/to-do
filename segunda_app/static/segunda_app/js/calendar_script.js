document.addEventListener("DOMContentLoaded", function() {
    const commitmentsDiv = document.querySelector("#commitments");
    let selectedDateISO = null; // Variável global para armazenar a data selecionada

    // Função para carregar compromissos de um dia específico
    function loadCommitments(dateStr) {
        fetch(`/agenda/get_commitments/?date=${dateStr}`)
            .then(response => response.json())
            .then(data => {
                commitmentsDiv.innerHTML = '';  // Limpa a div de compromissos
                if (data.compromissos && data.compromissos.length > 0) {
                    renderCommitments(data.compromissos);
                } else {
                    commitmentsDiv.innerHTML = '<p>Nenhum evento para esse dia.</p>';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar compromissos:', error);
                commitmentsDiv.innerHTML = '<p>Ocorreu um erro ao carregar os compromissos.</p>';
            });
    }

    // Função para renderizar compromissos na interface
    function renderCommitments(compromissos) {
        compromissos.forEach(comp => {
            const commitmentItem = document.createElement("div");
            commitmentItem.className = 'commitment-item';  // Classe para estilizar
            commitmentItem.innerHTML = `
                <strong>${comp.processo}</strong><br>
                <span>Local: ${comp.local}</span><br>
                <span>Início: ${comp.hora_inicio}</span><br>
                <span>Fim: ${comp.hora_fim}</span><br>
                <p>${comp.observacoes}</p>
                <button class="edit-button" data-id="${comp.id}">Editar</button>
                <button class="delete-button" data-id="${comp.id}">Excluir</button>
            `;
            commitmentsDiv.appendChild(commitmentItem);
        });

        // Garante a rolagem vertical
        commitmentsDiv.style.overflowY = 'auto';

        // Adiciona evento de clique para cada botão de excluir
        document.querySelectorAll('.delete-button').forEach(button => {
            button.addEventListener('click', function() {
                const compId = this.getAttribute('data-id'); // Obtém o ID do compromisso
                deleteCommitment(compId); // Chama a função para deletar o compromisso
            });
        });

        // Adiciona evento de clique para cada botão de editar
        document.querySelectorAll('.edit-button').forEach(button => {
            button.addEventListener('click', function() {
                const compId = this.getAttribute('data-id'); // Obtém o ID do compromisso
                // Redireciona para a página de edição
                window.location.href = `/agenda/editar_compromisso/${compId}/`;
            });
        });
    }

    // Função para excluir um compromisso
    function deleteCommitment(compId) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch(`/agenda/delete_commitment/${compId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Adiciona o token CSRF aqui
            }
        })
        .then(response => {
            if (response.ok) {
                // Remove o compromisso da interface
                const commitmentItem = document.querySelector(`.delete-button[data-id="${compId}"]`).parentElement;
                commitmentItem.remove();

                // Verifica se ainda há compromissos no dia
                if (commitmentsDiv.children.length === 0) {
                    commitmentsDiv.innerHTML = '<p>Nenhum evento para esse dia.</p>';

                    // Remove a data da lista de datas com compromissos
                    const selectedDate = selectedDateISO; // A data selecionada no formato 'YYYY-MM-DD'
                    const index = datasComCompromissos.indexOf(selectedDate);
                    if (index > -1) {
                        datasComCompromissos.splice(index, 1);
                    }

                    // Remove a bolinha verde do calendário
                    removeEventMarker(selectedDate);
                }
            } else {
                return response.json().then(err => {
                    console.error('Erro ao excluir o compromisso:', err.error);
                    alert(`Erro: ${err.error}`);
                });
            }
        })
        .catch(error => {
            console.error('Erro ao fazer a requisição para excluir o compromisso:', error);
        });
    }

    // Função para remover o marcador de evento (bolinha verde) do calendário
    function removeEventMarker(dateStr) {
        // Encontra o elemento do dia correspondente
        const dayElements = document.querySelectorAll('.flatpickr-day');
        dayElements.forEach(dayElem => {
            const dayDateStr = dayElem.dateObj.toISOString().split('T')[0];
            if (dayDateStr === dateStr) {
                // Remove o marcador de evento se existir
                const eventMarker = dayElem.querySelector('.event-marker');
                if (eventMarker) {
                    eventMarker.remove();
                }
            }
        });
    }

    // Configura o calendário flatpickr
    const calendar = flatpickr("#datepicker", {
        locale: "pt",              // Idioma para português
        dateFormat: "d/m/Y",       // Formato da data
        inline: true,              // Exibe o calendário inline (não em modal)
        defaultDate: "today",      // Data padrão (hoje)
        firstDayOfWeek: 1,         // Começa a semana na segunda-feira
        onDayCreate: function(dObj, dStr, fp, dayElem) {
            const dateStr = dayElem.dateObj.toISOString().split('T')[0];  // 'YYYY-MM-DD'

            if (datasComCompromissos.includes(dateStr)) {
                const eventMarker = document.createElement('div');
                eventMarker.className = 'event-marker';  // Classe do marcador de evento
                dayElem.appendChild(eventMarker);
            }

            // Adiciona o listener de clique no próprio dia
            dayElem.addEventListener("click", function() {
                selectedDateISO = dateStr; // Atualiza a data selecionada
                loadCommitments(dateStr);  // Carrega compromissos quando o dia é clicado
            });
        }
    });
});
