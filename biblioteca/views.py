from django.db.models.functions import Concat
from django.db.models import F, Value
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from biblioteca.models import Livro, Categoria, Autor, Emprestimo
from biblioteca.serializers import LivroSerializer, CategoriaSerializer, AuthorSerializer, SuperuserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny 
from rest_framework.pagination import PageNumberPagination
from biblioteca.permissions import IsOwner
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied


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
        qs = self.queryset
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
            return [IsAdminUser()]
    
    
class AutorViewSet(ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AuthorSerializer
    
    def get_queryset(self):
        qs = self.queryset
        nome = self.request.query_params.get('nome_autor', None)
        if nome:
            qs = qs.filter(nome__icontains=nome)
            
        return qs
    
    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        if self.request.method in ['POST', 'DELETE', 'PATCH', 'PUT']:
            return [IsAdminUser()]
        return super().get_permissions()
    

class SuperuserViewSet(ModelViewSet):
    queryset = User.objects.filter(is_superuser=True)
    serializer_class = SuperuserSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['post', 'patch']
    
    def get_object(self):
        user = self.request.user
        if not user.is_superuser:
            raise PermissionDenied("Você não tem permissão para acessar este recurso.")
        return user
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Superuser created successfully."}, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Os dados foram atualizados com sucesso."}, status=status.HTTP_200_OK)
