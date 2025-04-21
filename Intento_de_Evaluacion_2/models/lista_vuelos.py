class NodoVuelo:
    def __init__(self, vuelo):
        self.vuelo = vuelo
        self.siguiente = None
        self.anterior = None

class ListaVuelos:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.longitud = 0

    def insertar_al_frente(self, vuelo):
        """Vuelo de emergencia"""
        nuevo_nodo = NodoVuelo(vuelo)
        if not self.cabeza:
            self.cabeza = self.cola = nuevo_nodo
        else:
            nuevo_nodo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo_nodo
            self.cabeza = nuevo_nodo
        self.longitud += 1

    def insertar_al_final(self, vuelo):
        """Enviar vuelo al final de la lista"""
        nuevo_nodo = NodoVuelo(vuelo)
        if not self.cola:
            self.cabeza = self.cola = nuevo_nodo
        else:
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self.longitud += 1

    def obtener_primero(self):
        """Primer vuelo de la lista"""
        return self.cabeza.vuelo if self.cabeza else None

    def obtener_ultimo(self):
        """Ultimo vuelo de la lista"""
        return self.cola.vuelo if self.cola else None

    def __len__(self):
        """Numero total de vuelos en la lista"""
        return self.longitud

    def insertar_en_posicion(self, vuelo, posicion):
        """Cambiar vuelo en posición específica"""
        if posicion < 0 or posicion > self.longitud:
            raise IndexError("Posición fuera de rango")
            
        nuevo_nodo = NodoVuelo(vuelo)
        
        # Lista vacia
        if not self.cabeza:
            self.cabeza = self.cola = nuevo_nodo
        # Insertar al frente
        elif posicion == 0:
            nuevo_nodo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo_nodo
            self.cabeza = nuevo_nodo
        # Insertar al final
        elif posicion == self.longitud:
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        # Insertar en medio
        else:
            actual = self.cabeza
            for _ in range(posicion - 1):
                actual = actual.siguiente
            
            nuevo_nodo.siguiente = actual.siguiente
            nuevo_nodo.anterior = actual
            actual.siguiente.anterior = nuevo_nodo
            actual.siguiente = nuevo_nodo
        
        self.longitud += 1

    def extraer_de_posicion(self, posicion):
        """Remueve un vuelo y retorna el vuelo en la posición dada"""
        if posicion < 0 or posicion >= self.longitud:
            raise IndexError("Posición fuera de rango")
        
        actual = self.cabeza
        for _ in range(posicion):
            actual = actual.siguiente
        
        # Desconectar el nodo
        if actual.anterior:
            actual.anterior.siguiente = actual.siguiente
        else:  # Era el primer nodo
            self.cabeza = actual.siguiente
            
        if actual.siguiente:
            actual.siguiente.anterior = actual.anterior
        else:  # Era el último nodo
            self.cola = actual.anterior
        
        self.longitud -= 1
        return actual.vuelo
    def listar_vuelos(self):
        """Lista de todos los vuelos en orden"""
        vuelos = []
        actual = self.cabeza
        while actual:
            vuelos.append(actual.vuelo)
            actual = actual.siguiente
        return vuelos