from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json
from site_app.dao import models
from django.db.models import Max
from rastreio_carne_ufv import blockchain_connect
import hashlib
from django.forms.models import model_to_dict

def cadastro_fazenda(request):
    if request.user.is_authenticated:
        return render(request, 'cadastro_fazenda.html', {"logado": 1})
    return HttpResponseRedirect("/login")


def salvar_fazenda(request):
    if request.method == "POST":
        nomeFazenda = request.POST.get("nome_fazenda")
        localizacaoFazenda = request.POST.get("localizacao_fazenda")
        tipoCriacao = request.POST.get("tipo_criacao")
        idFazenda = proximoIdFazenda()
        if not verificaFazenda(nomeFazenda):
            msg = "FAZENDA EXISTENTE"
            task_id = -1
        else:
            novaFazenda = models.Fazenda(
                id_fazenda=idFazenda,
                nome_fazenda=nomeFazenda,
                localizacao_fazenda=localizacaoFazenda,
                tipo_criacao=tipoCriacao
            )
            json_gen_hash = model_to_dict(novaFazenda)
            valor_hash = hashlib.md5(str(json_gen_hash).encode())
            task = blockchain_connect.setDado.delay(valor_hash.hexdigest(), json_gen_hash, 1)
            msg = "OK"
            task_id = task.id
    return HttpResponse(json.dumps({'resposta': msg, 'task_id': task_id}))


def proximoIdFazenda():
    fazendas = models.Fazenda.objects.all()
    if len(fazendas) == 0:
        return 1

    proximoId = int(fazendas.aggregate(Max('id_fazenda'))["id_fazenda__max"]) + 1
    return proximoId

def verificaFazenda(nome):
    retorno = models.Fazenda.objects.filter(nome_fazenda=nome)
    if len(retorno) > 0:
        return False
    return True
