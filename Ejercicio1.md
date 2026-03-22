Considerando lo visto en clase, definimos de manera precisa qué entendemos por "tablero solución" para el 8-puzzle.

## Definiciones

Definimos **tablero canónico** al tablero

`1 2 3 / 4 5 6 / 7 8 ?`

donde `?` representa la posición vacía. Los números se leen de izquierda a derecha y de arriba hacia abajo; el símbolo `/` separa filas.

Definimos **vecinos** de un número como los números a los que puede llegarse moviéndose hacia arriba, abajo, izquierda o derecha, es decir, ortogonalmente y sin salir del tablero. En consecuencia, cada número tiene como mínimo 2 vecinos y como máximo 4.

Por ejemplo, en el tablero canónico, los vecinos del `1` son `2` y `4`, mientras que los vecinos del `6` son `3`, `5` y `?`.

## Tablero resuelto

Definimos **tablero resuelto** como todo tablero en el que se preservan las relaciones de vecindad del tablero canónico. Más precisamente, un tablero está resuelto si, para cada par de símbolos `a` y `b` entre `{1, 2, 3, 4, 5, 6, 7, 8, ?}`, se cumple que:

`a` y `b` son vecinos en el tablero canónico si y solo si `a` y `b` son vecinos en el tablero actual.

Es decir, la condición objetivo no exige una única disposición fija de las fichas, sino la preservación exacta de las adyacencias del tablero canónico.

## Representación del estado

Como estructura de estado, representaremos un tablero mediante un arreglo `board` de 9 enteros.

Para cada celda `c` en `{0, 1, ..., 8}`, `board[c]` indica qué ficha ocupa dicha celda. Usaremos el número `0` para representar el agujero, es decir, el símbolo `?`.

Por lo tanto:

- `board` tiene longitud 9.
- `board` es una permutación de `{0, 1, 2, 3, 4, 5, 6, 7, 8}`.
- la celda `0` corresponde a la esquina superior izquierda;
- la celda `1`, a la posición inmediatamente a su derecha;
- y así sucesivamente, en orden fila por fila.

Definimos, para una celda `c`:

- `fila(c) = c div 3`
- `col(c) = c mod 3`

donde `div` denota división entera.

La posición actual de una ficha `x` puede obtenerse como el único índice `pos(x)` tal que `board[pos(x)] = x`.

Con esta notación, decimos que dos números `x` e `y` son vecinos si

`abs(fila(pos(x)) - fila(pos(y))) + abs(col(pos(x)) - col(pos(y))) = 1`.

## Generación de sucesores

A partir de un estado actual, conseguir nuevos estados válidos también es simple. Sea `h` la única celda tal que `board[h] = 0`, es decir, la posición actual del agujero.

Un movimiento válido consiste en **swappear** el agujero con una de las fichas ubicadas en una celda vecina ortogonal a `h`. En otras palabras, si una celda `c` es vecina ortogonal de `h`, entonces puede generarse un nuevo estado intercambiando `board[h]` y `board[c]`.

De este modo, cada sucesor se obtiene a partir del estado actual mediante un único intercambio entre el agujero y una ficha vecina.

## Observación sobre la representación

Esta elección es natural en este problema porque el estado queda completamente determinado por el contenido de cada celda. Además, a partir de `board` puede recuperarse sin ambigüedad la posición de cualquier ficha, y por lo tanto también puede verificarse la condición objetivo formulada en términos de adyacencias.

Mantener además un arreglo inverso `pos`, tal que `pos[x]` indique la celda ocupada por la ficha `x`, no es estrictamente necesario, aunque puede simplificar la generación de sucesores y algunas operaciones auxiliares. Sin embargo, la representación principal del estado será `board`, entendido como un arreglo de 9 enteros.

## Espacio de estados

Como `board` es una permutación de los 9 símbolos `{0, 1, 2, 3, 4, 5, 6, 7, 8}`, el espacio de estados total tiene tamaño

`9! = 362880`.

Cada estado representa una configuración posible del tablero, independientemente de que sea o no alcanzable desde un estado inicial dado.

Se puede demostrar que bajo las operaciones descritas a realizar en un tablero, la paridad de la cantidad de inversiones del tablero 'aplanado' es invariante. Por ello, surgen 2 clases de tablero, dependiendo de si la cantidad de inversiones en su versión aplanada es par o impar, respectivamente.

Si además se consideran únicamente los estados alcanzables mediante movidas válidas a partir de un estado inicial fijo, entonces no se recorren los `362880` estados, sino solamente una de las dos componentes de alcanzabilidad del 8-puzzle. En consecuencia, desde un estado inicial fijo pueden alcanzarse

`9! / 2 = 181440`

estados.

Esta partición en dos componentes se debe a la restricción de paridad propia del problema: una movida válida preserva la clase de alcanzabilidad del tablero, y por eso no todos los tableros pueden transformarse entre sí.

## Cantidad de soluciones

Bajo la definición adoptada de **tablero resuelto**, no existe una única solución, sino varias.

En total hay exactamente **8 tableros resueltos**. Estos 8 tableros son precisamente las configuraciones que preservan las adyacencias del tablero canónico, y corresponden a sus 8 simetrías geométricas: identidad, rotaciones y reflexiones.

Por lo tanto, la condición objetivo no define un único estado meta, sino un conjunto de 8 estados meta.

Ahora bien, dado un estado inicial fijo, no necesariamente las 8 soluciones pertenecen a la misma componente de alcanzabilidad. Debido a la paridad mencionada antes, desde un estado inicial concreto solo serán alcanzables las soluciones que queden en su misma componente. En particular, las 8 soluciones se reparten en partes iguales entre las dos componentes, de modo que desde un estado inicial fijo habrá **4 soluciones alcanzables**.

## Heurísticas admisibles no triviales

Como la condición objetivo no está dada por un único tablero meta sino por un conjunto de 8 tableros resueltos, toda heurística debe considerar ese conjunto completo. En particular, si `G` es el conjunto de tableros solución, una forma natural de construir heurísticas admisibles consiste en evaluar un costo estimado respecto de cada tablero de `G` y tomar el mínimo.

### Heurística 1: cantidad de fichas fuera de lugar

Para cada tablero meta `g` en `G`, definimos:

`h_mis_g(board) =` cantidad de fichas entre `1` y `8` que no están en la misma celda que en `g`.

Luego definimos la heurística

`h1(board) = min { h_mis_g(board) : g en G }`.

Esta heurística es **admisible** porque en una movida válida solo se desplaza una ficha numerada. En consecuencia, la cantidad de fichas fuera de lugar puede disminuir a lo sumo en 1 por movida. Por lo tanto, si hay `k` fichas fuera de lugar respecto del mejor tablero meta posible, se necesitan al menos `k` movidas para alcanzar una solución.

### Heurística 2: suma de distancias Manhattan

Para cada ficha `x` entre `1` y `8`, y para cada tablero meta `g` en `G`, sea `pos_g(x)` la celda que ocupa `x` en `g`. Definimos:

`h_man_g(board) = suma, para x entre 1 y 8, de |fila(pos(x)) - fila(pos_g(x))| + |col(pos(x)) - col(pos_g(x))|`.

Luego definimos la heurística

`h2(board) = min { h_man_g(board) : g en G }`.

Esta heurística es **admisible** porque en cada movida válida solo una ficha numerada cambia de posición, y su distancia Manhattan a la celda objetivo puede variar a lo sumo en 1. En consecuencia, la suma total de distancias Manhattan nunca puede disminuir más de una unidad por movida. Por lo tanto, esa suma constituye una cota inferior sobre la cantidad real de movimientos necesarios.

Además, `h2` suele ser más informativa que `h1`, ya que no solo detecta si una ficha está mal ubicada, sino también cuán lejos se encuentra de su posición en el mejor tablero meta posible.

## Métodos de búsqueda recomendados

### A* con `h2`

El método de búsqueda principal a utilizar sería **A*** con la heurística `h2`.

La razón es que:

- el costo de cada movida es uniforme;
- `h2` es admisible;
- por lo tanto, A* es completo y óptimo;
- y, además, `h2` guía la búsqueda mucho mejor que una estrategia desinformada.

En este problema, A* con suma de distancias Manhattan resulta una elección natural porque combina garantía de optimalidad con una reducción importante del número de estados expandidos.

### A* con `h1`

Como alternativa también puede utilizarse **A*** con `h1`.

Esta opción sigue siendo completa y óptima, ya que `h1` también es admisible. Sin embargo, en general expandirá más nodos que A* con `h2`, porque proporciona una estimación menos precisa del costo restante.

Por ello, A* con `h1` puede tomarse como una línea base informada simple, mientras que A* con `h2` sería la variante preferida.

### BFS como línea base desinformada

Si se quisiera comparar contra una búsqueda desinformada, el método más razonable sería **BFS**.

La razón es que:

- explora por profundidad creciente;
- con costos uniformes encuentra soluciones óptimas;
- y sirve como referencia para medir cuánto mejora una búsqueda heurística.

Su principal desventaja es el consumo de memoria, ya que debe mantener una frontera grande aun en instancias moderadas.

### Greedy con `h2`

Si el objetivo principal fuera obtener una solución rápidamente, aun resignando optimalidad, podría utilizarse **Greedy** con `h2`.

Esta variante suele ser más veloz en la práctica, pero no garantiza encontrar la solución de menor costo. Por eso no sería el método principal si se busca optimalidad, aunque sí puede ser útil como comparación experimental.
