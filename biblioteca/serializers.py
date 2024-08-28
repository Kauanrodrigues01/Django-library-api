from rest_framework import serializers
from biblioteca.models import Livro, Categoria, Autor, Emprestimo
from biblioteca.validators import LivroValidate, EmprestimoValidate, AuthorValidate
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import re
import datetime

class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'descricao', 'data_publicacao', 'categoria_id', 'autor_id', 'categoria_nome', 'autor_nome', 'criador', 'criador_nome']
    
    criador_nome = serializers.CharField(max_length=100, read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), source='categoria')
    autor_id = serializers.PrimaryKeyRelatedField(queryset=Autor.objects.all(), source='autor')
    categoria_nome = serializers.SlugRelatedField(
        slug_field='nome',
        source='categoria',
        read_only=True
    )
    autor_nome = serializers.SlugRelatedField(
        slug_field='nome',
        source='autor',
        read_only=True
    )
    
    def validate(self, attrs):
        if self.instance:
            if attrs.get('descricao') is None:
                attrs['descricao'] = self.instance.descricao
            if attrs.get('data_publicacao') is None:
                attrs['data_publicacao'] = self.instance.data_publicacao
            if attrs.get('categoria') is None:
                attrs['categoria'] = self.instance.categoria
            if attrs.get('autor') is None:
                attrs['autor'] = self.instance.autor
                
        if attrs.get('titulo') is None and self.instance:
            attrs['titulo'] = self.instance.titulo
        else:
            if attrs['titulo'] in Livro.objects.values_list('titulo', flat=True):
                raise serializers.ValidationError('O titulo já está em uso!')
        
        LivroValidate(dados=attrs, ErrorClass=serializers.ValidationError)
        return attrs

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']
    
    def validate(self, attrs):
        if self.instance:
            if attrs.get('nome') is None:
                attrs['nome'] = self.instance.nome
                
        if attrs['nome'].isdigit():
            raise serializers.ValidationError('O nome da categoria não pode ser um número.')
        if attrs['nome'] == '':
            raise serializers.ValidationError('O nome da categoria não pode ser vazio.')
        if len(attrs['nome']) < 3:
            raise serializers.ValidationError('O nome da categoria deve ter no mínimo 3 caracteres.')
        if len(attrs['nome']) > 50:
            raise serializers.ValidationError('O nome da categoria deve ter no máximo 50 caracteres.')
        return attrs
    
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ['id', 'nome', 'biografia']
        
    def validate(self, attrs):
        if self.instance:
            attrs['nome'] = attrs.get('nome', self.instance.nome)
            attrs['biografia'] = attrs.get('biografia', self.instance.biografia)
        
        AuthorValidate(dados=attrs, ErrorClass=serializers.ValidationError)
        
        return attrs

class SuperuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': False},
            'username': {'required': True}
        }

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=False)
    
    def create(self, validated_data):
        user = User.objects.create_superuser(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data.get('email', '')
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
    
    def validate(self, attrs):
        first_name = attrs.get('first_name', '')
        last_name = attrs.get('last_name', '').split()
        if not first_name.isalpha():
            raise serializers.ValidationError({'error_first_name':'O first_name nome deve conter apenas letras.'})
        for nome in last_name:
            if not nome.isalpha():
                raise serializers.ValidationError({'error_last_name':'O last_name nome deve conter apenas letras.'})
        return super().validate(attrs)

class EmprestimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo
        fields = ['id', 'livro', 'usuario', 'data_inicio', 'data_prevista_devolucao', 'devolvido']
        
    livro = serializers.PrimaryKeyRelatedField(queryset=Livro.objects.all())
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    def validate(self, attrs):
        # Data de início é gerada automaticamente pelo modelo, não é necessário no validate.
        # Remova 'data_inicio' de attrs
        attrs.pop('data_inicio', None)
        
        EmprestimoValidate(dados=attrs, ErrorClass=serializers.ValidationError)
        
        return attrs
    
    def create(self, validated_data):
        # Definindo data_inicio como hoje, pois é um campo gerado automaticamente.
        emprestimo = Emprestimo.objects.create(
            livro=validated_data['livro'],
            usuario=validated_data['usuario'],
            data_inicio=datetime.date.today(),  # Data de início é definida como hoje
            data_prevista_devolucao=validated_data['data_prevista_devolucao']
        )
        return emprestimo
    
    def partial_update(self, instance, validated_data):
        instance.devolvido = validated_data.get('devolvido', instance.devolvido)
        instance.data_prevista_devolucao = validated_data.get('data_prevista_devolucao', instance.data_prevista_devolucao)
        instance.save()
        return instance