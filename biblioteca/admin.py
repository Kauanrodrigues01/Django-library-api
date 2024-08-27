from django.contrib import admin
from biblioteca.models import *

# Register your models here.
class LivrosAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'data_publicacao', 'categoria', 'autor',)
    search_fields = ['titulo', 'categoria__nome', 'autor__nome'] # procurar pelo categoria__nome os __ significa acessar o campo de uma relação
    list_filter = ['categoria', 'autor']
    list_display_links = ['titulo']
    list_editable = ['data_publicacao']
    list_per_page = 10

admin.site.register(Livro, LivrosAdmin)

class CategoriasAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    list_display_links = ['nome']
    list_per_page = 10

admin.site.register(Categoria, CategoriasAdmin)

class AutorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    list_display_links = ['nome']
    list_per_page = 10
    
admin.site.register(Autor, AutorAdmin)