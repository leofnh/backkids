from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('home/', views.home),
    path('api/produtos/', views.produtos),
    path('api/clientes/', views.clientes),
    path('api/venda/', views.venda),
    path('api/dashboard/', views.dashboard),
    path('api/login/', views.login_app),
    path('api/import/products/', views.import_product),
    path('pdf/comprovante/<int:sale_id>/', views.print_receipt_view),
    path('api/venda/', views.venda),
    path('api/produtos/loja/', views.produtos_loja),
    path('api/add/carrinho/<int:usuario>/', views.carrinholoja),
    path('api/add/image/products/', views.send_image_product),
    path('api/pagar-me/', views.api_pagar_me),
    path('api/remove/item/sacola/', views.api_del_cart),
    path('api/create/user/', views.api_cadastro),
    path('api/meus/pedidos/<int:usuario>/', views.meus_pedidos),
    path('api/get/imgslide/', views.get_links_capa),
    path('api/config/aboutus/', views.aboutus),
    path('api/adm/condicional/', views.produto_condicional),
    path('api/add/produto-condicional/', views.add_produto_cond),
    path('api/del/img-produto/', views.del_img_link)
]
