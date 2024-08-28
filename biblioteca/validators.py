from collections import defaultdict
from django.core.exceptions import ValidationError
from datetime import datetime
from biblioteca.models import Livro, Emprestimo
import re


class LivroValidate:
    def __init__(self, dados, errors=None, ErrorClass=None) -> None:
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.dados = dados
        self.clean()
        
    def clean(self, *args, **kwargs):
        dados = self.dados
        
        titulo = dados.get('titulo')
        descricao = dados.get('descricao')
        data_publicacao = dados.get('data_publicacao')
        error_class = self.ErrorClass
        
        if titulo is None or descricao is None or data_publicacao is None:
            self.errors['missing_fields'].append('Os campos título, descrição e data de publicação são obrigatórios.')
        
        if len(titulo) < 5:
            self.errors['titulo'].append('O título deve ter mais de 5 caracteres.')
        
        if len(descricao) < 20:
            self.errors['descricao'].append('A descrição deve ter no mínimo 20 caracteres.')
        
        # Validação da data de publicação
        if isinstance(data_publicacao, datetime):
            data_publicacao = data_publicacao.date()

        if data_publicacao > datetime.now().date():
            self.errors['data_publicacao'].append('A data de publicação não pode ser no futuro.')
        
        if self.errors:
            raise error_class(self.errors)
        
class EmprestimoValidate:
    def __init__(self, dados, errors=None, ErrorClass=None) -> None:
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.dados = dados
        self.clean()
        
    def clean(self, *args, **kwargs):
        dados = self.dados
        error_class = self.ErrorClass
        
        data_inicio = dados.get('data_inicio')  # data_inicio não será obrigatório na validação
        data_prevista_devolucao = dados.get('data_prevista_devolucao')
        devolvido = dados.get('devolvido')
        
        if isinstance(data_prevista_devolucao, str):
            try:
                data_prevista_devolucao = datetime.strptime(data_prevista_devolucao, '%Y-%m-%d').date()
            except ValueError:
                self.errors['data_prevista_devolucao'].append('Formato de data inválido para data prevista de devolução.')
        elif isinstance(data_prevista_devolucao, datetime):
            data_prevista_devolucao = data_prevista_devolucao.date()

        # Validar se data_prevista_devolucao é posterior a data_inicio
        if data_inicio and data_prevista_devolucao:
            if data_prevista_devolucao <= data_inicio:
                self.errors['data_prevista_devolucao'].append(
                    'A data prevista de devolução deve ser posterior à data de início do empréstimo.'
                )
        elif data_prevista_devolucao is None:
            self.errors['data_prevista_devolucao'].append(
                'A data prevista de devolução deve ser fornecida.'
            )

        # Verificar se o empréstimo foi devolvido
        if devolvido:
            if data_inicio is None or data_prevista_devolucao is None:
                self.errors['devolvido'].append(
                    'Se o empréstimo foi devolvido, as datas de início e prevista de devolução devem estar definidas.'
                )

        if self.errors:
            raise error_class(self.errors)
        
class AuthorValidate:
    def __init__(self, dados, errors=None, ErrorClass=None) -> None:
        self.dados = dados
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.clean()
        
    def clean(self):
        dados = self.dados
        nome = dados.get('nome', '').strip() 
        biografia = dados.get('biografia', '').strip()
        error_class = self.ErrorClass
        
        if nome.isdigit():
            self.errors['nome'].append('O nome não pode ser apenas dígitos.')
        
        if re.search(r'\d', nome):
            self.errors['nome'].append('O nome não pode conter números.')

        if not nome:
            self.errors['nome'].append('O nome não pode estar vazio.')
        
        if biografia.isdigit():
            self.errors['biografia'].append('A biografia não pode ser apenas dígitos.')
        
        if not biografia:
            self.errors['biografia'].append('A biografia não pode estar vazia.')

        if self.errors:
            raise error_class(self.errors)