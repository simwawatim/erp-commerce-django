from base.models import Customer, SalesOrder, Product, InventoryTransaction, FinancialTransaction, Employee, Payroll, Product
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = ['id', 'user', 'role', 'profile_picture']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        employee = Employee.objects.create(user=user, **validated_data)
        return employee

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance
    

class GetProductByNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name']
    

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'quantity',
            'cost_per_unit',
            'is_available',
            'image',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]


class PayrollSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), write_only=True, source='employee'
    )

    class Meta:
        model = Payroll
        fields = [
            'id',
            'employee',       
            'employee_id',    
            'bonus',
            'deductions',
            'net_pay',
            'total_paid',
            'status',
            'pay_date'
        ]


        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = '__all__'

class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'

class FinancialTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialTransaction
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class SalesOrderCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )

    class Meta:
        model = SalesOrder
        fields = ['product_id', 'quantity']


class SalesOrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )


    class Meta:
        model = SalesOrder
        fields = [
            'id',
            'product',      
            'product_id',   
            'quantity',
            'price',
            'date_ordered'
        ]

class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'

class FinancialTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialTransaction
        fields = '__all__'


class GetEmployeeByNameSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'employee']


class UserProfileSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'employee']

    def update(self, instance, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_picture and hasattr(instance, 'employee'):
            instance.employee.profile_picture = profile_picture
            instance.employee.save()

        return instance



class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    name = serializers.CharField()
    address = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        # Create User
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        # Create Customer
        customer = Customer.objects.create(
            user=user,
            name=validated_data['name'],
            email=validated_data['email'],
            address=validated_data.get('address', '')
        )
        return customer

