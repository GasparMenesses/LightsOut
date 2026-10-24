"""
Proyecto Lights Out - Álgebra aplicada (UCU)

Resolución del juego Lights Out mediante un sistema lineal de ecuaciones
sobre el conjunto {0, 1} con suma binaria (1 + 1 = 0).

Convención de índices: la incógnita x_i, con
i - 1 = n*q + r y 0 <= r < n, corresponde a la luz a_(q+1)(r+1).
En Python (índices desde 0) eso es simplemente k = i - 1 = n*fila + columna.
"""


def construir_sistema(tablero):
    """Construye la matriz ampliada [A | b] del sistema para un tablero n x n.

    La fila k de A (asociada a la luz en (fila, col), con k = n*fila + col)
    tiene un 1 en la columna de cada luz que, al ser presionada, cambia el
    estado de esa luz: ella misma y sus vecinas arriba, abajo, izquierda y
    derecha (las que existan dentro del tablero).
    El término independiente b_k es el estado inicial de la luz: si está
    prendida (1) necesita un número impar de cambios; si está apagada (0),
    un número par.
    """
    n = len(tablero)
    if any(len(fila) != n for fila in tablero):
        raise ValueError("El tablero debe ser una matriz cuadrada n x n.")
    if any(v not in (0, 1) for fila in tablero for v in fila):
        raise ValueError("El tablero solo puede contener ceros y unos.")

    N = n * n
    ampliada = []
    for fila in range(n):
        for col in range(n):
            ecuacion = [0] * (N + 1)
            for df, dc in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                f, c = fila + df, col + dc
                if 0 <= f < n and 0 <= c < n:
                    ecuacion[n * f + c] = 1
            ecuacion[N] = tablero[fila][col]
            ampliada.append(ecuacion)
    return ampliada


def sumar_filas(destino, origen):
    """Transformación elemental F_i -> F_i + F_j con la suma binaria (1+1=0)."""
    return [(a + b) % 2 for a, b in zip(destino, origen)]


def escalerizar_binario(ampliada):
    """Escalerización gaussiana (forma escalerizada reducida) sobre {0, 1}.

    Como solo hay dos valores posibles, todo pivote no nulo vale 1 y no hace
    falta dividir: la única operación necesaria para anular entradas es
    F_i -> F_i + F_j. Si en la posición del pivote queda un 0, se le suma una
    fila de más abajo que tenga un 1 en esa columna (también F_i -> F_i + F_j),
    lo que evita tener que intercambiar filas.

    Devuelve la matriz escalerizada y la lista de columnas pivote.
    """
    M = [fila[:] for fila in ampliada]
    filas = len(M)
    columnas = len(M[0]) - 1  # sin contar el término independiente
    pivotes = []
    fila_actual = 0

    for col in range(columnas):
        # Buscar una fila con un 1 en esta columna, desde fila_actual hacia abajo
        p = next((f for f in range(fila_actual, filas) if M[f][col] == 1), None)
        if p is None:
            continue  # columna sin pivote -> variable libre
        if p != fila_actual:
            # En lugar de intercambiar filas, se suma la fila p a la actual
            # (F_actual -> F_actual + F_p): así el pivote pasa a valer 1 usando
            # solo la transformación elemental que nos pidieron en el enunciado.
            M[fila_actual] = sumar_filas(M[fila_actual], M[p])
        # Anular el resto de la columna (arriba y abajo) con F_i -> F_i + F_pivote
        for f in range(filas):
            if f != fila_actual and M[f][col] == 1:
                M[f] = sumar_filas(M[f], M[fila_actual])
        pivotes.append(col)
        fila_actual += 1
        if fila_actual == filas:
            break
    return M, pivotes


def resolver_lights_out(tablero):
    """Recibe una matriz n x n de 0 y 1 (estado inicial) y devuelve el vector
    solución v = (x_1, ..., x_{n^2}) de ceros y unos, donde x_i = 1 indica
    que hay que presionar la luz a_(q+1)(r+1), con i - 1 = n*q + r.

    Si el tablero no tiene solución, lanzamos ValueError.
    Si tiene más de una, se devuelve la que asigna 0 a las variables libres.
    """
    M, pivotes = escalerizar_binario(construir_sistema(tablero))
    N = len(M)

    # Sistema incompatible: una fila 0 = 1
    for fila in M:
        if all(v == 0 for v in fila[:N]) and fila[N] == 1:
            raise ValueError("Este tablero no tiene solución.")

    # En la forma escalerizada reducida cada pivote se despeja directamente
    # (las variables libres valen 0).
    x = [0] * N
    for f, col in enumerate(pivotes):
        x[col] = M[f][N]
    return x



# Funciones auxiliares para verificar resultados

def presionar(tablero, fila, col):
    """Devuelve el tablero resultante de presionar la luz (fila, col) (índices desde 0)."""
    n = len(tablero)
    nuevo = [f[:] for f in tablero]
    for df, dc in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        f, c = fila + df, col + dc
        if 0 <= f < n and 0 <= c < n:
            nuevo[f][c] = 1 - nuevo[f][c]
    return nuevo


def aplicar_solucion(tablero, x):
    """Aplica al tablero las jugadas indicadas por el vector x."""
    n = len(tablero)
    for k, v in enumerate(x):
        if v == 1:
            tablero = presionar(tablero, k // n, k % n)
    return tablero


def mostrar(tablero):
    for fila in tablero:
        print(" ".join(str(v) for v in fila))


if __name__ == "__main__":
    # Ejemplo 3x3 del enunciado
    tablero_3 = [[0, 1, 0],
                 [1, 1, 0],
                 [0, 0, 1]]
    x = resolver_lights_out(tablero_3)
    print("Tablero 3x3 del enunciado:")
    mostrar(tablero_3)
    print("Solución:", x)
    print("Tablero tras aplicar la solución:")
    mostrar(aplicar_solucion(tablero_3, x))
    print()

    # Ejemplo 5x5 del enunciado
    tablero_5 = [[0, 0, 1, 1, 1],
                 [0, 1, 1, 1, 0],
                 [1, 0, 0, 1, 1],
                 [1, 1, 0, 0, 1],
                 [0, 1, 1, 1, 0]]
    print("Tablero 5x5 del enunciado:")
    mostrar(tablero_5)
    try:
        x5 = resolver_lights_out(tablero_5)
        print("Solución:", x5)
        print("Luces a presionar:",
              [f"a{k // 5 + 1}{k % 5 + 1}" for k, v in enumerate(x5) if v])
        print("Tablero tras aplicar la solución:")
        mostrar(aplicar_solucion(tablero_5, x5))
    except ValueError as e:
        print(e)