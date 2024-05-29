from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


from .serializers import *
from .models import *
from ecommerce import api_messages as msg


class CustomerViewSet(viewsets.ModelViewSet):
    """
    User profile related operations.
    """
    queryset = User.objects.all()
    serializer_class = CustomerListSerializer
    http_method_names = ["get", "post", "put", "delete"]
    action_serializers = {
        "create": CustomerCreateSerializer,
        "list": CustomerListSerializer,
        "login": CustomerLoginSerializer,
        "update": CustomerUpdateSerializer,
        "change_password": ChangePasswordSerializer,
        "me": CustomerListSerializer
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, self.serializer_class)
    
    def get_authenticated_user(self):
        user = get_object_or_404(self.queryset, pk=self.request.user.pk)
        return user

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['create', 'login']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request):
        response = super(CustomerViewSet, self).list(request)
        return Response({"data": response.data, "message": msg.success}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        response = super(CustomerViewSet, self).retrieve(request)
        return Response({"data": response.data, "message": msg.success}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": serializer.data, "message": msg.user_added}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        response = super(CustomerViewSet, self).update(request, partial=True)
        return Response({"data": response.data, "message": msg.user_updated}, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        response = super(CustomerViewSet, self).destroy(request)
        return Response({"message": msg.user_deleted}, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=["post"], detail=False)
    def login(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            access_token = serializer.validated_data.get("access_token")
            return Response({"access_token": access_token, "message": msg.loged_in}, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def change_password(self, request):

        """This action will allow User to change/update thier password"""
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            new_password = serializer.validated_data['new_password']
            old_password = serializer.validated_data['old_password']

            if not user.check_password(old_password):
                return Response({"message": msg.old_password}, status=status.HTTP_401_UNAUTHORIZED)
        
            user.set_password(new_password)
            user.save()
            return Response({"message": msg.change_password}, status=status.HTTP_200_OK)
        else:
            return Response({"message": msg.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=["get"], detail=False)
    def me(self, request, pk=None):

        """get logged in user"""

        serializer = self.get_serializer(self.get_authenticated_user())
        return Response({"data": serializer.data, "message": msg.success}, status=status.HTTP_200_OK)
    


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product's CRUD operations.
    """
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [IsAuthenticated]
    action_serializers = {
        "create": ProductCreateSerializer,
        "list": ProductListSerializer,
        "update": ProductCreateSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, self.serializer_class)
    

    def list(self, request):
        response = super(ProductViewSet, self).list(request)
        return Response({"data": response.data, "message": msg.success}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        response = super(ProductViewSet, self).retrieve(request)
        return Response({"data": response.data, "message": msg.success}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": serializer.data, "message": msg.product_added}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        response = super(ProductViewSet, self).update(request, partial=True)
        return Response({"data": response.data, "message": msg.product_updated}, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        response = super(ProductViewSet, self).destroy(request)
        return Response({"message": msg.product_removed}, status=status.HTTP_204_NO_CONTENT)
    

class OrderViewSet(viewsets.ModelViewSet):
    """
    Order's CRUD operations.
    """
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    action_serializers = {
        "create": OrderCreateSerializer,
        "list": OrderListSerializer,
        "update": OrderUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, self.serializer_class)   

    def get_queryset(self):
        queryset = Order.objects.all()
        products = self.request.query_params.get('products')
        customer_name = self.request.query_params.get('customer')
        
        if products:
            product_names = products.split(',')
            queryset = queryset.filter(order_items__product__name__in=product_names).distinct()
        
        if customer_name:
            queryset = queryset.filter(customer__name=customer_name)
        
        return queryset

    def list(self, request):
        response = super(OrderViewSet, self).list(request)
        return Response({"data": response.data, "message": msg.success}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        response = super(OrderViewSet, self).retrieve(request)
        return Response({"data": response.data, "message": msg.success}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": serializer.data, "message": msg.order_created}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        response = super(OrderViewSet, self).update(request, partial=True)
        return Response({"data": response.data, "message": msg.order_updated}, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        response = super(OrderViewSet, self).destroy(request)
        return Response({"message": msg.order_deleted}, status=status.HTTP_204_NO_CONTENT)