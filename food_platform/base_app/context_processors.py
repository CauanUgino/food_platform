##ESSA FUNÇÃO CONTA OS PRODUTOS DO CARRINHO E RETORNA O TOTAL DE ITENS PARA SER USADO NO TEMPLATE
def cart_item_count(request):
    cart = request.session.get("cart", {})
    return {
        "cart_count": sum(item["quantity"] for item in cart.values())
    }
