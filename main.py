import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import paho.mqtt.client as mqtt
import uuid

# Carregar informações do arquivo JSON
with open('infos.json', 'r') as json_file:
    infos = json.load(json_file)["infos"]

BROKER = infos['BROKER']
PORT = infos['PORT']
TOPIC = infos['TOPIC']
USERNAME = infos['USERNAME']
PASSWORD = infos['PASSWORD']
CLIENT_ID = infos['CLIENT_ID']

# Dados iniciais
data_model = {
    "id": str(uuid.uuid4()),
    "data": {
        "typeModel": {
            "aspectTypes": [],
            "assetTypes": []
        },
        "instanceModel": {
            "assets": []
        },
        "mappingModel": {
            "mappings": []
        }
    }
}

# Funções MQTT
def on_connect(client, userdata, flags, rc):
    print(f'Conectado ao broker MQTT com código {rc}')
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f'Mensagem recebida: {msg.payload.decode()}')

client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)

# Funções para manipular o JSON
def adicionar_aspect():
    aspect_id = simpledialog.askstring("Adicionar Aspect", "Digite o ID do Aspect:")
    if aspect_id:
        description = simpledialog.askstring("Adicionar Aspect", "Digite a descrição do Aspect:")
        variables = []
        while True:
            var_name = simpledialog.askstring("Adicionar Variável", "Digite o nome da variável (ou deixe vazio para terminar):")
            if not var_name:
                break
            var_type = simpledialog.askstring("Adicionar Variável", "Digite o tipo da variável:")
            unit = simpledialog.askstring("Adicionar Variável", "Digite a unidade de medida:")
            variables.append({
                "name": var_name,
                "dataType": var_type,
                "qualityCode": True,
                "unit": unit,
                "searchable": False,
                "referenceId": f"{var_name}ReferenceId"
            })
        aspect = {
            "id": f"tenant.{aspect_id}",
            "name": aspect_id,
            "description": description,
            "category": "dynamic",
            "referenceId": f"{aspect_id}ReferenceId",
            "variables": variables
        }
        data_model["data"]["typeModel"]["aspectTypes"].append(aspect)
        atualizar_json()

def adicionar_type():
    type_id = simpledialog.askstring("Adicionar Type", "Digite o ID do Type:")
    if type_id:
        description = simpledialog.askstring("Adicionar Type", "Digite a descrição do Type:")
        aspects = []
        while True:
            aspect_name = simpledialog.askstring("Adicionar Aspect ao Type", "Digite o nome do Aspect (ou deixe vazio para terminar):")
            if not aspect_name:
                break
            aspect = next((a for a in data_model["data"]["typeModel"]["aspectTypes"] if a["name"] == aspect_name), None)
            if aspect:
                aspects.append({
                    "name": aspect_name,
                    "aspectTypeId": aspect["id"],
                    "referenceId": f"{aspect_name}ReferenceId"
                })
            else:
                messagebox.showinfo("Erro", "Aspect não encontrado.")
        asset_type = {
            "id": f"tenant.{type_id}",
            "name": type_id,
            "description": description,
            "parentTypeId": "core.basicasset",
            "variables": [],
            "referenceId": f"{type_id}ReferenceId",
            "aspects": aspects
        }
        data_model["data"]["typeModel"]["assetTypes"].append(asset_type)
        atualizar_json()

def adicionar_asset():
    asset_name = simpledialog.askstring("Adicionar Asset", "Digite o nome do Asset:")
    if asset_name:
        type_name = simpledialog.askstring("Adicionar Asset", "Digite o nome do Type:")
        asset_type = next((t for t in data_model["data"]["typeModel"]["assetTypes"] if t["name"] == type_name), None)
        if asset_type:
            asset = {
                "name": asset_name,
                "typeId": asset_type["id"],
                "parentReferenceId": "e67bd43eccf94502b9679747b0d682dc",
                "description": "",
                "referenceId": f"{asset_name}ReferenceId"
            }
            data_model["data"]["instanceModel"]["assets"].append(asset)
            atualizar_json()
        else:
            messagebox.showinfo("Erro", "Type não encontrado.")

def atualizar_json():
    with open('dados.json', 'w') as json_file:
        json.dump(data_model, json_file, indent=4)
    print("JSON atualizado.")

def enviar_mensagem():
    client.publish(TOPIC, json.dumps(data_model))
    print("Mensagem enviada via MQTT.")

def visualizar_json():
    with open('dados.json', 'r') as json_file:
        preview = json.load(json_file)
    preview_window = tk.Toplevel(root)
    preview_window.title("Preview do JSON")
    text = tk.Text(preview_window, wrap='word')
    text.insert('1.0', json.dumps(preview, indent=4))
    text.pack(padx=10, pady=10)

# Interface Gráfica
root = tk.Tk()
root.title("Editor de Itens MQTT")

frame = tk.Frame(root)
frame.pack(pady=20, padx=20)

btn_adicionar_aspect = tk.Button(frame, text="Adicionar Aspect", command=adicionar_aspect)
btn_adicionar_aspect.grid(row=0, column=0, padx=10, pady=10)

btn_adicionar_type = tk.Button(frame, text="Adicionar Type", command=adicionar_type)
btn_adicionar_type.grid(row=0, column=1, padx=10, pady=10)

btn_adicionar_asset = tk.Button(frame, text="Adicionar Asset", command=adicionar_asset)
btn_adicionar_asset.grid(row=0, column=2, padx=10, pady=10)

btn_visualizar_json = tk.Button(frame, text="Visualizar JSON", command=visualizar_json)
btn_visualizar_json.grid(row=1, column=0, padx=10, pady=10)

btn_enviar_mensagem = tk.Button(frame, text="Enviar Mensagem", command=enviar_mensagem)
btn_enviar_mensagem.grid(row=1, column=1, padx=10, pady=10)

# Iniciar o loop MQTT e Tkinter
client.loop_start()
root.mainloop()