from django.http import Http404
from base.models import Customer, SalesOrder, Product, InventoryTransaction, FinancialTransaction, Employee, Payroll, Product
from api.serializers.serializers import CustomerSerializer, EmployeeSerializer,FinancialTransactionSerializer, InventoryTransactionSerializer, ProductSerializer, PayrollSerializer, SalesOrderSerializer, UserSerializer,  GetProductByNameSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.models import User
from base.models import Employee
from django.db import transaction
from rest_framework import generics


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
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
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
        hourly_rate = request.data.get('hourly_rate')

        # Validate user_data presence and type
        if not user_data or not isinstance(user_data, dict):
            return Response({'error': 'User data is required and must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate all user fields are present and non-empty
        required_user_fields = ['username', 'first_name', 'last_name', 'email']
        for field in required_user_fields:
            if not user_data.get(field):
                return Response({'error': 'All user fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate role and hourly_rate
        if not role:
            return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)
        if hourly_rate is None:
            return Response({'error': 'Hourly rate is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize and create User
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            employee = Employee.objects.create(
                user=user,
                role=role,
                hourly_rate=hourly_rate
            )
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
        hourly_rate = request.data.get('hourly_rate')

        # Validate user_data presence and type
        if not user_data or not isinstance(user_data, dict):
            return Response({'error': 'User data is required and must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate all user fields present and non-empty
        required_user_fields = ['username', 'first_name', 'last_name', 'email']
        for field in required_user_fields:
            if not user_data.get(field):
                return Response({'error': 'All user fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate role and hourly_rate presence
        if not role:
            return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)
        if hourly_rate is None:
            return Response({'error': 'Hourly rate is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Update User
        user_serializer = UserSerializer(employee.user, data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update Employee
        employee.role = role
        employee.hourly_rate = hourly_rate
        employee.save()

        return Response(EmployeeSerializer(employee).data)

    def patch(self, request, pk):
        employee = self.get_object(pk)
        user_data = request.data.get('user', {})
        role = request.data.get('role', employee.role)
        hourly_rate = request.data.get('hourly_rate', employee.hourly_rate)

        # Update User (partial)
        user_serializer = UserSerializer(employee.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update Employee
        employee.role = role
        employee.hourly_rate = hourly_rate
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        payrolls = Payroll.objects.all()
        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PayrollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayrollDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        serializer = SalesOrderSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            if product.quantity < quantity:
                return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

            # Update product quantity
            product.quantity -= quantity
            product.save()

            # Save the sales order
            order = serializer.save()

            # Create financial transaction
            FinancialTransaction.objects.create(
                description=f"Sale: {product.name} x {quantity}",
                amount=quantity * serializer.validated_data['price'],
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
