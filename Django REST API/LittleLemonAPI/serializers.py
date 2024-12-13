from rest_framework import serializers
from .models import MenuItem, Cart, Category, Order, OrderItem
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CategorySerializer(serializers.ModelSerializer): 
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )


    def validate(self, attrs):
        if attrs['quantity'] < 1:
            raise ValidationError("Quantity must be greater than 0")
        attrs['unit_price'] = attrs['menuitem'].price
        attrs['price'] = attrs['quantity'] * attrs['unit_price']
        return attrs

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'unit_price', 'quantity', 'price']
        extra_kwargs = {
            'price': {'read_only': True},
            'unit_price': {'read_only': True}
        } 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']
        extra_kwargs = {
            'groups': {'read_only': True},
            'email': {'read_only': True}
        }
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["order", "menuitem", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    orderitem = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "status", "date", "total", "orderitem"]
        kwargs = {
            "orderitem": {"read_only": True},
            "total": {"read_only": True},
            "user": {"read_only": True},
            "date": {"read_only": True}
        }
