var camposValidosQualidade = false;

$("#salvar").click(function(event) {
    event.preventDefault();
    validaCamposQualidade();
    if (camposValidosQualidade) {
        $(".loader").toggle();
        $("#form_qualidade").submit();
    }
});

function validaCamposQualidade() {
    var idAnimal = $("#animal").val();
    var comprimentoSar = $("#comprimento_sarcomero").val();
    var forcaCis = $("#forca_cisalhamento").val();
    var perdaDesCong = $("#perda_descongelamento").val();
    var perdaCoccao = $("#perda_coccao").val();
    var corCarneL = $("#cor_carne_l").val();
    var corCarneA = $("#cor_carne_a").val();
    var corCarneB = $("#cor_carne_b").val();
    var corGorduraL = $("#cor_gordura_l").val();
    var corGorduraA = $("#cor_gordura_a").val();
    var corGorduraB = $("#cor_gordura_b").val();

    if (idAnimal != "" && comprimentoSar != "" && forcaCis != "" && perdaDesCong != "" && perdaCoccao != "" &&
        corCarneL != "" && corCarneA != "" && corCarneB != "" && corGorduraL != "" && corGorduraA != "" &&
        corGorduraB != "") {

        camposValidosQualidade = true;

    } else {
        alert("Campo(s) vazio(s) detectado(s)! Por favor, preencha todos os campos.");
    }
}

$("#voltar").click(function(event) {
    event.preventDefault();
    location.href = "/";
});

$(document).ready(function() {
    $('#form_qualidade').submit(function(event) {
        var formData = new FormData($(this)[0]);
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: formData,
            cache: false,
            contentType: false,
            enctype: 'multipart/form-data',
            processData: false,
            async: true,

            success: function(result) {
                result = JSON.parse(result);
                if (result.resposta == 'OK') {
                    getStatus(result.task_id);
                } else if (result.resposta == "QUALIDADE EXISTENTE") {
                    alert("Animal já cadastrado a uma qualidade!");
                } else {
                    alert("Erro interno! Tente novamente mais tarde.");
                }
            },
            fail: function(msg) {
                $(".loader").toggle();
                alert("Erro ao salvar!");
            },
            beforeSend: function() {},
            complete: function(msg) {},
            error: function(msg) {
                $(".loader").toggle();
                alert("Erro interno!");
            }
        });
        event.preventDefault();
    });
});

function getStatus(taskID) {
    $.ajax({
            url: `/tasks/${taskID}/`,
            method: 'GET'
        })
        .done((res) => {
            const taskStatus = res.task_status;

            if (taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') {
                $(".loader").toggle();
                const taskResult = res.task_result;
                console.log(taskResult);
                if (taskResult == "OK") {
                    alert("Qualidade cadastrada com sucesso!");
                    location.href = "/";
                } else if (taskResult == "ERRO_DADOS") {
                    alert("Erro no salvamento dos dados!");
                } else if (taskResult == "ERRO_BLOCKCHAIN") {
                    alert("Erro ao salvar o dado na blockchain!");
                } else {
                    alert("Erro interno durante a tarefa assíncrona!");
                }
            } else {
                setTimeout(function() {
                    getStatus(res.task_id);
                }, 1000);
            }
        })
        .fail((err) => {
            $(".loader").toggle();
            console.log(err);
            alert("Erro interno!");
        });
}