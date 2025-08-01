import random
from django.http import Http404
from base.models import Customer, SalesOrder, Product, InventoryTransaction, FinancialTransaction, Employee, Payroll, Product
from api.serializers.serializers import CustomerSerializer, EmployeeSerializer,FinancialTransactionSerializer, GetEmployeeByNameSerializer, InventoryTransactionSerializer, ProductSerializer, PayrollSerializer, RegisterSerializer, SalesOrderCreateSerializer, SalesOrderSerializer, UserProfileSerializer, UserSerializer,  GetProductByNameSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.models import User
from base.models import Employee
from django.db import transaction
from rest_framework import generics
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from django.db.models import Count, Sum
from django.db.models import Sum, F
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q



# -------------------------------
# Authentication and Authorization
# -------------------------------

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)

            role = 'unknown'


            if hasattr(user, 'employee') and user.employee is not None:
                role = user.employee.role if user.employee.role else 'employee'
            elif hasattr(user, 'customer') and user.customer is not None:
                role = 'customer'

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': role
                }
            })

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    

class EmployeeListCreateView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        employees = Employee.objects.select_related('user').all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        user_data = request.data.get('user')
        role = request.data.get('role')

        if not user_data or not isinstance(user_data, dict):
            return Response({'error': 'User data is required and must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)

        required_user_fields = ['username', 'first_name', 'last_name', 'email']
        for field in required_user_fields:
            if not user_data.get(field):
                return Response({'error': 'All user fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not role:
            return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)

        random_password = str(random.randint(1000, 9999))
        user_data['password'] = random_password

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()


            user.set_password(random_password)
            user.save()
            employee = Employee.objects.create(user=user, role=role)
            try:
                send_mail(
                    subject="Your Account Credentials",
                    message=f"Hello {user.first_name},\n\nYour account has been created.\nUsername: {user.username}\nPassword: {random_password}",
                    from_email=settings.EMAIL_HOST_USER,  
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                return Response({'error': f'User created, but failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(EmployeeSerializer(employee).data, status=status.HTTP_201_CREATED)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(Employee, pk=pk)

    def get(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request, pk):
        employee = self.get_object(pk)
        user_data = request.data.get('user')
        role = request.data.get('role')
  
        if not user_data or not isinstance(user_data, dict):
            return Response({'error': 'User data is required and must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)
        required_user_fields = ['username', 'first_name', 'last_name', 'email']
        for field in required_user_fields:
            if not user_data.get(field):
                return Response({'error': 'All user fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not role:
            return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)
       

        user_serializer = UserSerializer(employee.user, data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee.role = role
        employee.save()

        return Response(EmployeeSerializer(employee).data)

    def patch(self, request, pk):
        employee = self.get_object(pk)
        user_data = request.data.get('user', {})
        role = request.data.get('role', employee.role)


        user_serializer = UserSerializer(employee.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        employee.role = role
        employee.save()

        return Response(EmployeeSerializer(employee).data)

    def delete(self, request, pk):
        employee = self.get_object(pk)
        user = employee.user
        employee.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------------------


# -------------------------------
# Product Management
# -------------------------------

class ProductListCreateView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# -------------------------------


# -------------------------------
# Payroll Management
# -------------------------------

class PayrollListCreateView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        payrolls = Payroll.objects.all()
        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PayrollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # FinancialTransaction.objects.create(description=f"Pay For: {serializer.employee.f}", amount=serializer.total_paid, module='Payroll')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayrollDetailView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        serializer = PayrollSerializer(payroll)
        return Response(serializer.data)

    def put(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        serializer = PayrollSerializer(payroll, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        serializer = PayrollSerializer(payroll, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        payroll.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------------------


class CustomerListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------------------
# -------------------------------
# Sales Order Management
# -------------------------------


class SalesOrderAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]  
    def get(self, request):
        orders = SalesOrder.objects.all()
        serializer = SalesOrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
            serializer = SalesOrderCreateSerializer(data=request.data)
            if serializer.is_valid():
                product = serializer.validated_data['product']  # Already a Product instance
                quantity = serializer.validated_data['quantity']

                if product.quantity < quantity:
                    return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

                product.quantity -= quantity
                product.save()

                order = SalesOrder.objects.create(
                    product=product,
                    quantity=quantity,
                    price=product.cost_per_unit 
                )

                FinancialTransaction.objects.create(
                    description=f"Sale: {product.name} x {quantity}",
                    amount=quantity * product.cost_per_unit,
                    module='Sales'
                )

                return Response(SalesOrderSerializer(order).data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SalesOrderDetailAPIView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        serializer = SalesOrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        serializer = SalesOrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class FinancialTransactionList(APIView):
    def get(self, request):
        transactions = FinancialTransaction.objects.all().order_by('-timestamp')
        serializer = FinancialTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class FinancialTransactionDetail(APIView):
    def get_object(self, pk):
        try:
            return FinancialTransaction.objects.get(pk=pk)
        except FinancialTransaction.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        transaction = self.get_object(pk)
        serializer = FinancialTransactionSerializer(transaction)
        return Response(serializer.data)

    def delete(self, request, pk):
        transaction = self.get_object(pk)
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RevenueAPIView(APIView):
    def get(self, request):
        revenue = FinancialTransaction.objects.filter(module__iexact='sales').aggregate(
            total_revenue=Sum('amount')
        )['total_revenue'] or 0
        return Response({"revenue": revenue}, status=status.HTTP_200_OK)


class ExpenseAPIView(APIView):
    def get(self, request):
        expense = FinancialTransaction.objects.exclude(module__iexact='sales').aggregate(
            total_expense=Sum('amount')
        )['total_expense'] or 0
        payroll_expense = Payroll.objects.filter(status='Paid').aggregate(
            total_payroll=Sum('total_paid')
        )['total_payroll'] or 0

        total_expense = expense + payroll_expense

        return Response({"expenses": total_expense}, status=status.HTTP_200_OK)


class ProfitAPIView(APIView):
    def get(self, request):
        revenue = FinancialTransaction.objects.filter(module__iexact='sales').aggregate(
            total_revenue=Sum('amount')
        )['total_revenue'] or 0

        expense = FinancialTransaction.objects.exclude(module__iexact='sales').aggregate(
            total_expense=Sum('amount')
        )['total_expense'] or 0

        payroll_expense = Payroll.objects.filter(status='Paid').aggregate(
            total_payroll=Sum('total_paid')
        )['total_payroll'] or 0

        total_expense = expense + payroll_expense
        profit = revenue - total_expense

        return Response({"profit": profit}, status=status.HTTP_200_OK)
class GetProductByName(APIView):
    def get(self, request):
        products = Product.objects.all() 
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
class GetEmployeeByNameView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializers = GetEmployeeByNameSerializer(users, many=True)
        return Response(serializers.data)
    


class GetEmployeeProfileView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DashboardStatsAPIView(APIView):

    def get(self, request):
        # HR: Employee count by role
        employee_by_role = (
            Employee.objects.values('role')
            .annotate(count=Count('id'))
            .order_by('role')
        )

        # Payroll: status distribution
        payroll_statuses = (
            Payroll.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        # Payroll: last 6 months net_pay totals
        six_months_ago = now() - timedelta(days=180)
        payroll_totals = (
            Payroll.objects.filter(pay_date__gte=six_months_ago)
            .extra(select={'month': "strftime('%%Y-%%m', pay_date)"})
            .values('month')
            .annotate(total=Sum('net_pay'))
            .order_by('month')
        )

        # Finance: total per module
        finance_modules = (
            FinancialTransaction.objects.values('module')
            .annotate(total=Sum('amount'))
            .order_by('module')
        )

        # Sales: total revenue per product
        sales_totals = (
            SalesOrder.objects.values('product__name')
            .annotate(total=Sum('price'))
            .order_by('-total')[:5]
        )

        # Inventory: total available products
        inventory_summary = {
            'total_products': Product.objects.count(),
            'available_products': Product.objects.filter(is_available=True).count()
        }

        # Overall system summary
        summary = {
            'total_employees': Employee.objects.count(),
            'total_products': Product.objects.count(),
            'total_sales': SalesOrder.objects.aggregate(Sum('price'))['price__sum'] or 0,
            'total_financial_activity': FinancialTransaction.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        }

        return Response({
            'hr': list(employee_by_role),
            'payroll_status': list(payroll_statuses),
            'payroll_trends': list(payroll_totals),
            'finance': list(finance_modules),
            'sales': list(sales_totals),
            'inventory': inventory_summary,
            'summary': summary,
        })
    



class BuyProducts(APIView):
    def post(self, request):
        try:
            items = request.data.get('items', [])
            full_name = request.data.get('name')
            email = request.data.get('email')
            address = request.data.get('address')

            if not items:
                return Response({"error": "No items provided."}, status=status.HTTP_400_BAD_REQUEST)

            if request.user.is_authenticated:
    
                customer_qs = Customer.objects.filter(user=request.user)
                if customer_qs.exists():
                    customer = customer_qs.first()
                else:
                    customer = Customer.objects.create(
                        user=request.user,
                        name=request.user.get_full_name() or request.user.username,
                        email=request.user.email,
                        address=address or ""
                    )
            else:
                if not full_name or not email or not address:
                    return Response({"error": "Guest checkout requires name, email, and address."},
                                    status=status.HTTP_400_BAD_REQUEST)
                customer_qs = Customer.objects.filter(email=email)
                if customer_qs.exists():
                    customer = customer_qs.first()
                    if not customer.address and address:
                        customer.address = address
                        customer.save()
                else:
                    customer = Customer.objects.create(
                        name=full_name,
                        email=email,
                        address=address
                    )

            total_order_price = Decimal('0.00')
            sales_orders = []

            # Use atomic transaction to ensure consistency
            with transaction.atomic():
                for item in items:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity', 1)

                    try:
                        quantity = int(quantity)
                        if quantity <= 0:
                            return Response({"error": f"Invalid quantity for product {product_id}."},
                                            status=status.HTTP_400_BAD_REQUEST)
                    except (ValueError, TypeError):
                        return Response({"error": f"Invalid quantity for product {product_id}."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    try:
                        product = Product.objects.select_for_update().get(id=product_id)
                    except Product.DoesNotExist:
                        return Response({"error": f"Product with ID {product_id} not found."},
                                        status=status.HTTP_404_NOT_FOUND)

                    if not product.quantity or product.quantity < quantity:
                        return Response({"error": f"Not enough stock for product {product.name}."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    total_price = Decimal(product.cost_per_unit or 0) * quantity
                    total_order_price += total_price

                    sales_order = SalesOrder.objects.create(
                        product=product,
                        quantity=quantity,
                        price=total_price,
                        customer=customer,
                        shipping_address=address if not request.user.is_authenticated else customer.address
                    )

                    product.quantity -= quantity
                    product.save()

                    FinancialTransaction.objects.create(
                        description=f"Sold {quantity} x {product.name} to {customer.name}",
                        amount=total_price,
                        module="Sales"
                    )

                    sales_orders.append({
                        "order_id": sales_order.id,
                        "product_name": product.name,
                        "quantity": quantity,
                        "total_price": f"{total_price:.2f}"
                    })

            return Response({
                "message": "Purchase successful.",
                "total_order_price": f"{total_order_price:.2f}",
                "orders": sales_orders
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ProductSalesSummaryAPIView(APIView):
    def get(self, request):
        # Total products count
        total_products = Product.objects.count()

        # Total quantity in stock (sum of quantity field)
        total_quantity = Product.objects.aggregate(total=Sum('quantity'))['total'] or 0

        # Total sales amount (sum of quantity * price in SalesOrder)
        total_sales_amount = SalesOrder.objects.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0

        # Pie chart data: top 5 products by sales amount
        sales_by_product = (
            SalesOrder.objects
            .values('product__name')
            .annotate(total_sales=Sum(F('quantity') * F('price')))
            .order_by('-total_sales')[:5]
        )
        pie_chart = [
            {"name": item['product__name'], "value": item['total_sales']}
            for item in sales_by_product
        ]

        # Quarterly sales aggregation
        quarters = {1: 0, 2: 0, 3: 0, 4: 0}
        for order in SalesOrder.objects.all():
            quarter = (order.date_ordered.month - 1) // 3 + 1
            quarters[quarter] += order.quantity * order.price

        bar_chart = [
            {"name": f"Q{q}", "sales": amount}
            for q, amount in sorted(quarters.items())
        ]

        data = {
            "cards": [
                {"label": "Total Products", "value": total_products},
                {"label": "Total Quantity in Stock", "value": total_quantity},
                {"label": "Total Sales Amount", "value": total_sales_amount},
            ],
            "pieChart": pie_chart,
            "barChart": bar_chart,
        }

        return Response(data)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({"message": "Customer registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserCustomerAPIView(APIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(customer)
        return Response(serializer.data)
    


class EmployeeSummaryAPIView(APIView):
    def get(self, request):
        role_counts = (
            Employee.objects
            .values('role')
            .annotate(count=Count('id'))
            .order_by('role')
        )
        
        roles = dict(Employee.ROLE_CHOICES)
        data = {role: 0 for role in roles.keys()}
        
        for item in role_counts:
            data[item['role']] = item['count']
        
        # Prepare labels and counts for graph
        labels = [roles[role] for role in data.keys()]
        counts = list(data.values())
        
        return Response({
            "totals": data,  
            "graph": {
                "labels": labels,
                "counts": counts
            }
        })
    

class SalesSummaryAPIView(APIView):
    def get(self, request):
        now = timezone.now()
        five_months_ago = (now - timedelta(days=150)).replace(day=1)

        total_sales_agg = SalesOrder.objects.aggregate(
            total_sales=Sum(F('price') * F('quantity'))
        )
        total_sales = total_sales_agg['total_sales'] or 0

        total_orders = SalesOrder.objects.count()
        two_days_ago = now - timedelta(days=2)
        pending_orders = SalesOrder.objects.filter(date_ordered__gte=two_days_ago).count()

        monthly_sales_qs = (
            SalesOrder.objects
            .filter(date_ordered__gte=five_months_ago)
            .annotate(month=TruncMonth('date_ordered'))
            .values('month')
            .annotate(total=Sum(F('price') * F('quantity')))
            .order_by('month')
        )
        months = []
        for i in range(4, -1, -1):
            m = (now - timedelta(days=30*i)).strftime("%b %Y")
            months.append(m)
        sales_by_month = {entry['month'].strftime("%b %Y"): float(entry['total'] or 0) for entry in monthly_sales_qs}
        monthly_sales = [sales_by_month.get(month, 0) for month in months]

        data = {
            "total_sales": total_sales,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "monthly_sales": {
                "labels": months,
                "data": monthly_sales,
            }
        }
        return Response(data)
    
class FinanceSummaryAPI(APIView):
    def get(self, request):
        total_income = FinancialTransaction.objects.filter(amount__gt=0).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = FinancialTransaction.objects.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = abs(total_expense) 

        six_months_ago = now().replace(day=1)
        monthly_qs = (
            FinancialTransaction.objects
            .filter(timestamp__gte=six_months_ago)
            .annotate(month=TruncMonth('timestamp'))
            .values('month')
            .annotate(
                income=Sum('amount', filter=Q(amount__gt=0)),
                expense=Sum('amount', filter=Q(amount__lt=0))
            )
            .order_by('month')
        )

        labels = []
        incomes = []
        expenses = []

        for item in monthly_qs:
            labels.append(item['month'].strftime('%b %Y'))
            incomes.append(float(item['income'] or 0))
            expenses.append(abs(float(item['expense'] or 0)))

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'monthly_data': {
                'labels': labels,
                'income': incomes,
                'expense': expenses,
            }
        })