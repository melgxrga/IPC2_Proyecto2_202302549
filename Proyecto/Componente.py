class Componente:
    def __init__(self, linea, numero):
        self.linea = linea
        self.numero = numero
        
    def __str__(self):
        return f'Componente({self.linea}, {self.numero})'

    def __repr__(self):
        return f'Componente({self.linea}, {self.numero})'