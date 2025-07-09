from django.urls import path
from base import views
from api.views import LoginView, PayrollDetailView, PayrollListCreateView, ProductDetailView, ProductListCreateView
from .views import (
    BuyProducts, CustomerListCreateView, CustomerDetailView, DashboardStatsAPIView,  EmployeeListCreateView, EmployeeDetailView, ExpenseAPIView, FinancialTransactionDetail, FinancialTransactionList, GetEmployeeByNameView, GetEmployeeProfileView, GetProductByName, ProductSalesSummaryAPIView, ProfitAPIView, RegisterView, RevenueAPIView, SalesOrderAPIView, SalesOrderDetailAPIView,

)

urlpatterns = [
    
    path('api/employees/', EmployeeListCreateView.as_view()),
    path('api/employees/<int:pk>/', EmployeeDetailView.as_view()),
    path('api/products/', ProductListCreateView.as_view()),
    path('api/products/<int:pk>/', ProductDetailView.as_view()),
    path('api/payrolls/', PayrollListCreateView.as_view(), name='payroll-list-create'),
    path('api/payrolls/<int:pk>/', PayrollDetailView.as_view(), name='payroll-detail'),
    path('api/auth/login/', LoginView.as_view(), name='api-login'),
    path('api/customers/<int:pk>/', CustomerDetailView.as_view()),
    path('api/customers/', CustomerListCreateView.as_view()),
    path('api/sales-orders/', SalesOrderAPIView.as_view(), name='sales-orders'),
    path('api/sales-orders/<int:pk>/', SalesOrderDetailAPIView.as_view(), name='sales-order-detail'),
    path('api/financial-transactions/', FinancialTransactionList.as_view(), name='financialtransaction-list'),
    path('api/financial-transactions/<int:pk>/', FinancialTransactionDetail.as_view(), name='financialtransaction-detail'),
    path('api/financial/revenue/', RevenueAPIView.as_view(), name='revenue'),
    path('api/financial/expenses/', ExpenseAPIView.as_view(), name='expenses'),
    path('api/financial/profit/', ProfitAPIView.as_view(), name='profit'),
    path('api/get-product-by-name/', GetProductByName.as_view()),
    path('api/get-employee-by-name/', GetEmployeeByNameView.as_view()),
    path('api/profile/<int:pk>/', GetEmployeeProfileView.as_view()),
    path('api/dashboard-stats/', DashboardStatsAPIView.as_view()),
    path('api/buy/', BuyProducts.as_view(), name='buy-products'),
    path('api/product-sales-summary/', ProductSalesSummaryAPIView.as_view(), name='product-sales-summary'),
    path('api/register/', RegisterView.as_view(), name='register'),

   
]
