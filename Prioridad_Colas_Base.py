from Excepciones import SinPropiedad

# Definimos la clase base
class Prioridad_Colas:
    """Clase base para colas de prioridad"""
    def __init__(self):
        pass

    def add(self, key, value):
        raise NotImplementedError("Metodo add no implementado")

    def min(self):
        raise NotImplementedError("Metodo min no implementado")

    def remove_min(self):
        raise NotImplementedError("Metodo remove_min no implementado")

# Usamos esa clase base
class Item:
    """Contenedor de clave/valor"""
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __lt__(self, other):
        return self.key < other.key

class PrioridadColaSorted(Prioridad_Colas):
    """Cola de prioridad implementada con lista ordenada"""
    
    def __init__(self):
        self.data = []

    def __len__(self):
        return len(self.data)

    def is_empty(self):
        return len(self.data) == 0

    def add(self, key, value):
        """Agrega un nuevo item y lo inserta en el lugar correcto según su prioridad"""
        newest = Item(key, value)
        index = 0
        while index < len(self.data) and newest > self.data[index]:
            index += 1
        self.data.insert(index, newest)

    def min(self):
        if self.is_empty():
            raise SinPropiedad("La cola de prioridad está vacía")
        item = self.data[0]
        return (item.key, item.value)

    def remove_min(self):
        if self.is_empty():
            raise SinPropiedad("La cola de prioridad está vacía")
        item = self.data.pop(0)
        return (item.key, item.value)

    def ver_todo(self):
        return [{"prioridad": item.key, "valor": item.value} for item in self.data]