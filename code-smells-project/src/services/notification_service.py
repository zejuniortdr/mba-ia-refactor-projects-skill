"""Notificações de domínio (simuladas via print).

Isola os efeitos colaterais de notificação para fora dos controllers,
tornando-os reutilizáveis e substituíveis por integrações reais.
"""


def notificar_pedido_criado(pedido_id, usuario_id):
    print(f"ENVIANDO EMAIL: Pedido {pedido_id} criado para usuario {usuario_id}")
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")


def notificar_mudanca_status(pedido_id, novo_status):
    if novo_status == "aprovado":
        print(f"NOTIFICAÇÃO: Pedido {pedido_id} foi aprovado! Preparar envio.")
    if novo_status == "cancelado":
        print(f"NOTIFICAÇÃO: Pedido {pedido_id} cancelado. Devolver estoque.")
