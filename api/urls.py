from django.urls import path
from base import views
from api.views import LoginView, PayrollDetailView, PayrollListCreateView, ProductDetailView, ProductListCreateView
from .views import (
    CustomerListCreateView, CustomerDetailView,  EmployeeListCreateView, EmployeeDetailView,
    SalesOrderListCreateView, SalesOrderDetailView,
    InventoryTransactionListCreateView, InventoryTransactionDetailView,
    FinancialTransactionListCreateView, FinancialTransactionDetailView,
)

urlpatterns = [
    
   path('api/financial-transactions/<int:pk>/', FinancialTransactionDetailView.as_view()),
   path('api/inventory-transactions/<int:pk>/', InventoryTransactionDetailView.as_view()),
   path('api/employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
   path('api/employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
   path('api/products/', ProductListCreateView.as_view(), name='product-list-create'),
   path('api/products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
   path('api/payrolls/', PayrollListCreateView.as_view(), name='payroll-list-create'),
   path('api/payrolls/<int:pk>/', PayrollDetailView.as_view(), name='payroll-detail'),
   path('api/inventory-transactions/', InventoryTransactionListCreateView.as_view()),
   path('api/financial-transactions/', FinancialTransactionListCreateView.as_view()),
   path('api/sales-orders/<int:pk>/', SalesOrderDetailView.as_view()),
   path('api/auth/login/', LoginView.as_view(), name='api-login'),
   path('api/customers/<int:pk>/', CustomerDetailView.as_view()),
   path('api/sales-orders/', SalesOrderListCreateView.as_view()),
   path('api/customers/', CustomerListCreateView.as_view()),

   
]
