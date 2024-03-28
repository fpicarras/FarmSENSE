// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();


//  owl carousel script
$(".owl-carousel").owlCarousel({
    loop: true,
    margin: 20,
    nav: true,
    navText: [],
    autoplay: true,
    autoplayHoverPause: true,
    responsive: {
        0: {
            items: 1
        },
        1000: {
            items: 2
        }
    }
});

function goBack() {
    window.history.back();
}

document.getElementById("seeMoreBtn").addEventListener("click", function() {
    window.location.href = "ws_temp.html";
});

function expandirCaixa(idCaixa) {
    // Verifica se já existe uma caixa expandida
    if (document.getElementById('caixaExpandida')) {
        return; // Sai da função se já houver uma caixa expandida
    }

    var novaCaixa = document.createElement('div');
    novaCaixa.id = 'caixaExpandida';
    novaCaixa.style.width = '450px';
    novaCaixa.style.height = '450px';
    novaCaixa.style.background = '#f2f2f2'; // Alterado para um fundo acizentado
    novaCaixa.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
    novaCaixa.style.position = 'fixed';
    novaCaixa.style.top = '50%';
    novaCaixa.style.left = '50%';
    novaCaixa.style.transform = 'translate(-50%, -50%) scale(0.8)';
    novaCaixa.style.opacity = '0'; // Inicialmente transparente
    novaCaixa.style.zIndex = '9999';
    novaCaixa.style.padding = '40px'; // Ajusta a margem interna da caixa
    novaCaixa.style.transition = 'opacity 0.5s ease-in-out, transform 0.5s ease-in-out'; // Transições com o mesmo tempo
    novaCaixa.style.borderRadius = '8px';
    novaCaixa.style.transformStyle = 'preserve-3d';
    novaCaixa.style.perspective = '1000px';
    novaCaixa.style.overflowY = 'auto';
    novaCaixa.style.overflowX = 'auto';
    novaCaixa.style.textAlign = 'justify'; // Texto justificado automaticamente
    novaCaixa.style.lineHeight = '1.5'; // Espaçamento entre linhas
    novaCaixa.style.wordWrap = 'break-word'; // Quebra de palavra
    novaCaixa.style.margin = '50px'; // Adiciona margem de 50px

    var conteudo = document.getElementById(idCaixa).dataset.textoCompleto;
    novaCaixa.innerHTML = conteudo;

    var linkClose = document.createElement('span');
    linkClose.innerHTML = '<i class="fa-solid fa-x"></i>'; // Adiciona o símbolo 'X'
    linkClose.style.marginRight = '10px';
    linkClose.style.fontSize = '20px'; // Define o tamanho da fonte
    linkClose.style.position = 'absolute';
    linkClose.style.top = '10px';
    linkClose.style.right = '10px'; // Ajusta a posição para o canto superior direito
    linkClose.style.cursor = 'pointer';
    linkClose.onclick = function() {
        novaCaixa.style.opacity = '0'; // Torna a caixa transparente
        novaCaixa.style.transform = 'translate(-50%, -50%) scale(0.8)'; // Reduz a escala da caixa
        setTimeout(function() {
            document.body.removeChild(novaCaixa);
        }, 500); // Tempo igual ao da transição
    };
    
    linkClose.style.color = 'rgba(0, 0, 0, 0.5)'; // Defina uma cor inicial com alguma transparência

    linkClose.onmouseover = function() {
        linkClose.style.color = 'rgba(0, 0, 0, 0.8)'; // Torna a cor mais escura quando o mouse passa por cima
    };

    linkClose.onmouseout = function() {
        linkClose.style.color = 'rgba(0, 0, 0, 0.5)'; // Retorna a cor original quando o mouse sai
    };

    novaCaixa.appendChild(linkClose);

    // Adicionando o event listener para fechar a caixa quando o mouse sair dela
    novaCaixa.addEventListener('mouseout', function(event) {
        // Verifica se o evento mouseout ocorreu quando o ponteiro não está sobre a própria caixa
        if (!novaCaixa.contains(event.relatedTarget)) {
            novaCaixa.style.opacity = '0'; // Torna a caixa transparente
            novaCaixa.style.transform = 'translate(-50%, -50%) scale(0.8)'; // Reduz a escala da caixa
            setTimeout(function() {
                document.body.removeChild(novaCaixa);
            }, 500); // Tempo igual ao da transição
        }
    });

    // Adiciona um pequeno atraso antes de aplicar a escala completa e a opacidade total
    setTimeout(function() {
        novaCaixa.style.transform = 'translate(-50%, -50%) scale(1)';
        novaCaixa.style.opacity = '1';
    }, 10);

    document.body.appendChild(novaCaixa);
}
