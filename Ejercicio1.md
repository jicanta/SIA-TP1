Considerando lo visto en clase, vamos a definir concretamente qué consideramos como "tablero solución":
primero algunas definiciones:
definimos "tablero canónico" al tablero 1 2 3 \ 4 5 6 \ 7 8 ?, donde ? representa la posición vacía y leemos los números de izquierda a derecha, donde un '\' representa una nueva fila.
definimos 'vecinos' de un número como los, como mínimo 2 y a lo sumo 4, números a los que podemos llegar moviéndonos hacia arriba, abajo, derecha e izquierda (es decir, ortogonalmente) sin 'salirnos' del tablero.
Por ejemplo, en el tablero canónico, los vecinos del 1 son 2 y 4 y los vecinos del 6 son 3, 5 y ?.
Ahora bien, definamos "tablero resuelto":
decimos que un tablero está resuelto si para cada número entre 1 y 8 y también para el ?, los vecinos se preservan. Es decir, en el tablero canónico a y b son vecinos si y solo si en el tablero resuelto a y b también lo son.
Con todo ya definido, pasamos a la consigna per se.

Como estructura de estado, tendríamos un vector que para cierto número i, me indique la posición actual en el tablero del número i (asumiendo que el número 0 representa el agujero).
De esta forma, determinar si dos números dados son vecinos, es trivial. Para un número x, vamos a tomar fila(x) como ceil(pos[x]/3) y col(x) como pos[x] mod 3. Decimos que dos números x e y son vecinos entonces si abs(fila(x)-fila(y))+abs(col(x)-col(y)) = 1.
A su vez, conseguir nuevos estados válidos a partir de un estado actual también es facil. Consideremos pos[0] (la posición del agujero). Un movimiento válido consiste en 'swappear' al agujero con uno de sus vecinos ortogonales. Por lo tanto, como ya vimos que conseguir vecinos es trivial, realizar nuevas movidas también lo será.
Se puede representar el estado únicamente mediante un arreglo pos tal que pos[x] indique la celda ocupada por la ficha x, incluyendo al agujero como una ficha más. Esta representación es suficiente porque determina completamente la configuración del tablero: conocer la posición de cada ficha equivale a conocer qué ficha ocupa cada celda.

Esta elección es natural en este problema porque la condición objetivo está formulada en términos de adyacencias entre fichas, no de contenido por celda. Así, verificar si dos piezas son vecinas y calcular heurísticas basadas en adyacencias o distancias resulta directo a partir de pos.

Mantener además un arreglo inverso board no es estrictamente necesario, aunque puede simplificar la generación de sucesores y algunas operaciones auxiliares.