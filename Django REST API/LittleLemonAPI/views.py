from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category, MenuItem, Cart, Order, OrderItem
from . import serializers
from rest_framework.response import Response
from .permissions import IsManager 
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render
import math
from datetime import date
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
class CategoryListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class MenuItemListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    search_fields = ["category__title"]
    permission_classes = [IsAuthenticated]

    
    def get_permissions(self):
        permission_classes = [IsAuthenticated] 
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]
        


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer 
    def get_permissions(self):
        permission_classes = [IsAuthenticated] 
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]
    


class CartListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = serializers.CartSerializer 
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response("200 - Ok")

    
class ManagerView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    def get_queryset(self):
        return User.objects.all().filter(groups__name="Manager")
    
    def post(self, request, pk=None):
        user = get_object_or_404(User, username=request.data['username'])
        user.is_staff = True
        managers = Group.objects.get(name="Manager")
        managers.user_set.add(user)
        return Response("201 - Created") 
    

class ManagerDestroyView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    def get_queryset(self):
        return User.objects.all().filter(groups__name="Manager")
    
    def delete(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk)
            managers = Group.objects.get(name="Manager")
            try:
                managers.user_set.remove(user)
                return Response("200 - Success")
            except:
                return Response("404 - Not Found")
        else:
            return Response("400 - Bad request")
    

class DeliveryView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    def get_queryset(self):
        return User.objects.all().filter(groups__name="Delivery crew")
    
    def post(self, request, pk=None):
        user = get_object_or_404(User, username=request.data['username'])
        delivery = Group.objects.get(name="Delivery crew")
        delivery.user_set.add(user)
        return Response("201 - Created") 
    

class DeliveryDestroyView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    def get_queryset(self):
        return User.objects.all().filter(groups__name="Delivery crew")
    
    def delete(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk)
            delivery = Group.objects.get(name="Delivery crew")
            try:
                delivery.user_set.remove(user)
                return Response("200 - Success")
            except:
                return Response("404 - Not Found")
        else:
            return Response("400 - Bad request")
        
class OrderListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.user.groups.filter(name="Manager").exists():
            return Order.objects.all()
        elif self.request.user.groups.filter(name="Delivery crew").exists():
            return Order.objects.all().filter(delivery_crew=self.request.user)
        else:
            return Order.objects.all().filter(user=self.request.user)
    def post(self, request):
        order = Order.objects.create(user=self.request.user, total=0, date=date.today())
        cart = Cart.objects.all().filter(user=self.request.user)
        total = 0
        if not len(cart.values_list()):
            return Response({"message" : "empty cart"})
        for item in cart.values():
            total += item['price']
            OrderItem.objects.create(order=order, menuitem_id=item['menuitem_id'], quantity=item['quantity'], price=item['price'])
        order.total = total
        order.save()
        
        Cart.objects.all().filter(user=self.request.user).delete()

        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
 

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()
    
    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order.user!=request.user and not request.user.groups.filter(name="Manager").exists():
            return Response("403 - Forbidden")
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user.groups.filter(name="Manager").exists():
            order.status = not order.status
            order.save()
            return Response("200 - Ok")
        elif request.user.groups.filter(name="Delivery crew").exists() and order.delivery_crew==request.user:
            order.status = not order.status
            order.save()
            return Response("200 - Ok")
        else:
            return Response("403 - Unauthorized")
        
    def put(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.groups.filter(name="Manager").exists():
            return Response("403 - Unauthorized")
        order.delivery_crew = get_object_or_404(User, pk=request.data['delivery_crew'])
        order.status = not order.status
        order.save()
        return Response("200 - Ok")
    
    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.groups.filter(name="Manager").exists():
            return Response("403 - Unauthorized")
        order.delete()
        return Response("200 - Ok") 
        
        
        
        
        