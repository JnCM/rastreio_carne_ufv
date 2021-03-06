from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json
from datetime import datetime
from site_app.dao import models
from site_app.utils import utils
from django.db.models import Max
from rastreio_carne_ufv import blockchain_connect, settings
import hashlib
from django.forms.models import model_to_dict


def cadastro_comercializacao(request):
    if request.user.is_authenticated:
        embalagens = list(models.Embalagem.objects.all().order_by("data_embalagem").values())
        for embalagem in embalagens:
            save_data = embalagem["data_embalagem"]
            embalagem["data_embalagem"] = embalagem["data_embalagem"].strftime("%Y-%m-%d")
            hash_tb = list(models.Hash.objects.filter(id_tabela=10, id_item=str(embalagem['id_embalagem'])).values('id_hash_blockchain'))
            id_hash = hash_tb[0]['id_hash_blockchain']
            dado_hash = blockchain_connect.getDado(id_hash)
            hash_embalagem = hashlib.md5(str(embalagem).encode()).hexdigest()
            if hash_embalagem == dado_hash:
                embalagem['check_blockchain'] = True
            else:
                embalagem['check_blockchain'] = False  
            embalagem["data_embalagem"] = save_data
        return render(request, 'cadastro_comercializacao.html', {'embalagens': embalagens, "logado": 1})
    return HttpResponseRedirect("/login")


def salvar_comercializacao(request):
    if request.method == "POST":
        dataVenda = request.POST.get("data_venda")
        listaEmbalagens = json.loads(request.POST.get("lista_embalagens"))
        
        idComercializacao = proximoIdComercializacao()
        novaComercializacao = models.Comercializacao(
            id_comercializacao=idComercializacao,
            data_venda=dataVenda
        )
        json_gen_hash = model_to_dict(novaComercializacao)
        valor_hash = hashlib.md5(str(json_gen_hash).encode())
        task = blockchain_connect.setDado.delay(valor_hash.hexdigest(), json_gen_hash, 11)
        task_id_comercializacao = task.id
        i = 0
        j = 0
        tasks_ids = []
        for idEmbalagem in listaEmbalagens:
            if not verificaEmbalagem(idEmbalagem):
                msg = "COMERCIALIZACAO EXISTENTE"
                tasks_ids.append({"resposta": msg, "id_embalagem": i, "task_id": -1})
            else:
                if j == 0:
                    idItem = proximoIdItemComercializacao()
                else:
                    idItem += 1
                novaComercializacaoEmbalagem = models.ComercializacaoEmbalagem(
                    id_item=idItem,
                    id_embalagem=int(idEmbalagem),
                    id_comercializacao=idComercializacao
                )
                json_gen_hash = model_to_dict(novaComercializacaoEmbalagem)
                valor_hash = hashlib.md5(str(json_gen_hash).encode())
                task = blockchain_connect.setDado.delay(valor_hash.hexdigest(), json_gen_hash, 12)
                msg = "OK"
                tasks_ids.append({"resposta": msg, "id_embalagem": i, "task_id": task.id})
                j += 1
            i += 1
    return HttpResponse(json.dumps({"resposta": "OK", "task_id_comercializacao": task_id_comercializacao, "tasks_ids": tasks_ids}))


def proximoIdComercializacao():
    comercializacoes = models.Comercializacao.objects.all()
    if len(comercializacoes) == 0:
        proximoIdComercializacao = 1
    else:
        proximoIdComercializacao = int(comercializacoes.aggregate(Max('id_comercializacao'))["id_comercializacao__max"]) + 1
    return proximoIdComercializacao

def proximoIdItemComercializacao():
    comercializacoesEmbalagens = models.ComercializacaoEmbalagem.objects.all()
    if len(comercializacoesEmbalagens) == 0:
        proximoIdItem = 1
    else:
        proximoIdItem = int(comercializacoesEmbalagens.aggregate(Max('id_item'))["id_item__max"]) + 1

    return proximoIdItem

def verificaEmbalagem(idEmbalagem):
    retorno = models.ComercializacaoEmbalagem.objects.filter(id_embalagem=idEmbalagem)
    if len(retorno) > 0:
        return False
    return True
