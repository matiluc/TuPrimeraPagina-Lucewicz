Python y Django


Curso: Python Flex

Comisión: #78110


Profesor: Alan Exequiel Prestia


Alumno: Matias Lucewicz

LinkedIn: [/matiaslucewicz](https://www.linkedin.com/in/matiaslucewicz/)


Funcionalidades:

· Home: De las clases Receta y Suscriptor en models hago un .objects.count() en views para mostrar los totales de cada uno.

· Recetas: Con un for y "'detalle_receta' receta.pk" muestro cada contenido de la bbdd, limitando la visibilidad a 6 y mostrando las siguientes 6 con el botón hasta concluir el total. Se puede acceder a cada elemento gracias a un get_object_or_404 y la pk obtenida del for. Tambien se muestran las etiquetas gracias a la clase Categorias (incluida tambien dentro de la clase Receta y alli incluido un ManyToManyField) el cual tiene su propia bbdd con categorías fijas (sin tacc, vegetariano, etc) que se podrán elegir al momento de cargar una receta nueva.

· Nueva receta: Es un formulario al cual le agregué CKEditor para poder darle estilo al texto y carga de imagenes (también está disponible en el admin de django). Las funciones del mismo fueron definidas en settings. Lo mismo para la ubicación de imágenes en /media/. Se pueden elegir varias categorías gracias a SelectMultiple en la clase.

· Newsletter: Formulario normal que permite al usuario registrar sus datos en una bbdd para recibir posibles newsletters y que además, luego de suscribirse, devuelve una alerta de suscripción exitosa con un messages.success importado desde django.contrib.

· Pauta: Del TP.

· Buscar: Función que permite buscar las recetas segun el contenido total o parcial del título de cada receta (en algun momento lo extenderé a poder buscar segun el contenido de la receta en si y en las etiquetas de Categorías) que devuelve otro html pero con el resultado.