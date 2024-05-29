from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone


from .models import *
from .validators import password_validator



class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'contact_number']


class CustomerCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, validators=[password_validator])

    class Meta:
        model = User
        fields = ['name', 'email', 'contact_number', 'password']
    
    def validate_email(self, value):        
        email = value.lower()
        user = User.objects.filter(email=email).first()
        if user:
            raise serializers.ValidationError("Email already taken.")
        return email
    
    def validate_name(self, value):
        name = value.lower()
        if User.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError("Name already taken.")
        return value
    
    def validate(self, data):
        confirm_password = self.initial_data.get('confirm_password')
        if data['password'] != confirm_password:
            raise serializers.ValidationError("Password and confirm password don't match")

        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'contact_number']


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username").lower()
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        refresh =RefreshToken.for_user(user)

        data["access_token"] = str(refresh.access_token)
        return data
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[password_validator])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password doesn't match.")
        return data


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'weight']

    def validate_name(self, value):
        name = value.lower()
        if Product.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError("Product name already taken.")
        return value

    def validate_weight(self, value):
        if value <= 0 or value > 25:
            raise serializers.ValidationError("Weight must be positive and not more than 25kg.")
        return value
    

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'weight']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']


class OrderCreateSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer', 'order_date', 'address', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def validate_order_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Order date cannot be in the past.")
        return value

    def validate(self, data):
        total_weight = 0
        for item in data['order_items']:
            product = item['product']
            total_weight += product.weight * item['quantity']
        if total_weight > 150:
            raise serializers.ValidationError("Order cumulative weight must be under 150kg.")
        return data


class OrderUpdateSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_date', 'address', 'order_items']

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_items')
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        instance.order_items.all().delete()
        for item_data in order_items_data:
            OrderItem.objects.create(order=instance, **item_data)

        return instance

    def validate_order_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Order date cannot be in the past.")
        return value

    def validate(self, data):
        total_weight = 0
        for item in data['order_items']:
            product = item['product']
            total_weight += product.weight * item['quantity']
        if total_weight > 150:
            raise serializers.ValidationError("Order cumulative weight must be under 150kg.")
        return data


class OrderListSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()
    order_items = serializers.StringRelatedField(many=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer', 'order_date', 'address', 'order_items', 'total_price']
    
    def get_total_price(self, obj):
        total_price = sum(item.product.price * item.quantity for item in obj.order_items.all())
        return total_price