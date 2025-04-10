
class ColaArray:
    def __init__(self):
        self.items = []

    def esta_vacia(self):
        return len(self.items) == 0

    def encolar(self, elemento):
        self.items.append(elemento)

    def desencolar(self):
        if not self.esta_vacia():
            return self.items.pop(0)

    def obtener_lista(self):
        return self.items.copy()

    def enqueue(self, mission):
        """Agregar mision al final (FIFO)"""
        self.items.append(mission)

    def dequeue(self):
        """Eliminar y retornar la primera mision"""
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def first(self):
        """Ver la primera mision sin removerla"""
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        """Ver si la cola esta vacia"""
        return len(self.items) == 0

    def size(self):
        """Obtener la cantidad de misiones en la cola"""
        return len(self.items)

    def ver_todo(self):
        """Devolver todas las misiones sin modificar"""
        return self.items.copy()

        