from rest_framework import serializers
from biblioteca.models import Livro, Categoria, Autor
from biblioteca.validators import LivroValidate, EmprestimoValidate, AuthorValidate
from django.core.exceptions import ValidationError
import re

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
        AuthorValidate(dados=attrs, ErrorClass=serializers.ValidationError)
        return attrs


        