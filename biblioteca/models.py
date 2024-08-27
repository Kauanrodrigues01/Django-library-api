from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=50, null=False, blank=False)
    
    def __str__(self):
        return self.nome

    def clean(self):
        super().clean()
        num_livros = self.livros.count()
        if num_livros > 100:
            raise ValidationError("A categoria não pode ter mais de 100 livros.")

class Autor(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    biografia = models.TextField(null=False, blank=False)
    
    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=100, null=False, blank=False)
    descricao = models.TextField(null=True, blank=True)
    data_publicacao = models.DateField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True, related_name='livros')
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, null=True, blank=True, related_name='livros')
    criador = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='livros_criados')
    
    def __str__(self):
        return self.titulo

    def clean(self):
        super().clean()
        if self.categoria:
            self.categoria.clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, null=False, blank=False, on_delete=models.CASCADE, related_name='emprestimos')
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='emprestimos')
    data_inicio = models.DateField(auto_now_add=True)  # O auto_now_add adiciona a data automaticamente no cadastro do empréstimo
    data_prevista_devolucao = models.DateField(null=False, blank=False)
    devolvido = models.BooleanField(default=False)

    def clean(self):
        if self.data_prevista_devolucao <= self.data_inicio:
            raise ValidationError("A data prevista de devolução deve ser posterior à data de início do empréstimo.")
        
        emprestimos_nao_devolvidos = Emprestimo.objects.filter(usuario=self.usuario, devolvido=False).count()
        if emprestimos_nao_devolvidos >= 5:
            raise ValidationError("O usuário já possui 5 empréstimos não devolvidos.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
