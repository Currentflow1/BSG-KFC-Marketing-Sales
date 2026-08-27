from django.urls import path
from . import views

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("search/", views.order_search, name="order_search"),

    path("add/", views.order_new, name="order_add"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("<int:order_id>/edit/", views.order_edit, name="order_edit"),
    path("<int:order_id>/delete/", views.order_delete, name="order_delete"),

    path("<int:order_id>/add-customer/", views.add_customer, name="add_customer"),
    path("<int:order_id>/customers/<int:customer_detail_id>/delete/", views.customer_delete, name="customer_delete"),
    path("order/<int:order_id>/customer-search/", views.customer_search, name="customer_search"),

    path("<int:order_id>/delivery/", views.manage_delivery, name="manage_delivery"),
    path("<int:order_id>/delivery/mload/", views.manage_delivery_mload, name="manage_delivery_mload"),
    path("<int:order_id>/delivery/mret/", views.manage_delivery_mret, name="manage_delivery_mret"),
    path("<int:order_id>/delivery/vbo/", views.manage_delivery_vbo, name="manage_delivery_vbo"),
    path("<int:order_id>/delivery/<int:line_id>/delete/", views.delivery_delete, name="delivery_delete"),
    path("<int:order_id>/delivery/set-order-type/", views.set_delivery_order_type, name="set_delivery_order_type"),
    path("order/<int:order_id>/product-search/", views.product_search, name="product_search"),

    path("<int:order_id>/transactions/", views.manage_transactions, name="manage_transactions"),
    path("<int:order_id>/customers/<int:customer_detail_id>/manage-transactions/", views.manage_transactions_for_customer, name="manage_transactions_for_customer"),
    path("<int:order_id>/transactions/<int:line_id>/delete/", views.transaction_delete, name="transaction_delete"),
    path("<int:order_id>/transactions/set-context/", views.set_transaction_context, name="set_transaction_context"),
    path("<int:order_id>/transactions/save-invoice-balance/", views.save_invoice_balance, name="save_invoice_balance"),
    path("order/<int:order_id>/transaction-customer-search/", views.transaction_customer_search, name="transaction_customer_search"),
    path("order/<int:order_id>/transaction-product-search/", views.transaction_product_search, name="transaction_product_search"),
]