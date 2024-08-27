from django.db.models.functions import Concat
from django.db.models import F, Value
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet
from biblioteca.models import Livro, Categoria
from biblioteca.serializers import LivroSerializer, CategoriaSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import PageNumberPagination
from biblioteca.permissions import IsOwner

class LivroViewPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.all().annotate(
        criador_nome=Concat(
            F('criador__first_name'), 
            Value(' '), 
            F('criador__last_name'), 
            Value(' ('),
            F('criador__username'),
            Value(')'))).select_related('categoria', 'autor', 'criador').order_by('-id')
    
    serializer_class = LivroSerializer
    pagination_class = LivroViewPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        titulo = self.request.query_params.get('titulo', None)
        categoria = self.request.query_params.get('categoria', None)
        autor = self.request.query_params.get('autor', None)
        if categoria:
            qs = qs.filter(categoria__nome__icontains=categoria)
        if autor:
            qs = qs.filter(autor__nome__icontains=autor)
        if titulo:
            qs = qs.filter(titulo__icontains=titulo)
        return qs
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsOwner(), IsAdminUser()]
        return [IsAuthenticated(), IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        request.data['criador'] = request.user.id
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(criador=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsOwner()]
    
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = Categoria.objects.filter(pk=pk).first()
        
        if instance is None:
            return Response(
                {"detail": "Categoria não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)