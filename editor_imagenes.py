import os
from PyQt5.QtWidgets import (
   QApplication, QWidget,
   QFileDialog,
   QLabel, QPushButton, QListWidget,
   QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt # Constante Qt.KeepAspectRatio para mantener proporciones al redimensionar
from PyQt5.QtGui import QPixmap # Formato de imagen optimizado para pantallas de Qt

from PIL import Image
from PIL import ImageQt # Permite convertir imágenes de Pillow directamente a formatos de Qt
from PIL import ImageFilter
# Importación de filtros predefinidos de Pillow para procesamiento de imágenes
from PIL.ImageFilter import (
   BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE,
   EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN,
   GaussianBlur, UnsharpMask
)

# === 1. CONFIGURACIÓN DE LA INTERFAZ GRÁFICA (UI) ===
app = QApplication([])
win = QWidget()       
win.resize(700, 500) 
win.setWindowTitle('Editor simple')

# Creación de los componentes (Widgets)
lb_image = QLabel("Imagen")
btn_dir = QPushButton("Carpeta")
lw_files = QListWidget()

btn_left = QPushButton("Izquierda")
btn_right = QPushButton("Derecha")
btn_flip = QPushButton("Reflejo")
btn_sharp = QPushButton("Nitidez")
btn_bw = QPushButton("B/N")

# Organización de los componentes en el espacio (Layouts)
row = QHBoxLayout()          # Contenedor horizontal principal
col1 = QVBoxLayout()         # Columna 1: Panel de archivos
col2 = QVBoxLayout()         # Columna 2: Visualizador e instrumentos

col1.addWidget(btn_dir)      
col1.addWidget(lw_files)     
col2.addWidget(lb_image, 95) # Da el 95% del espacio vertical a la imagen

row_tools = QHBoxLayout()    # Sub-contenedor horizontal para la barra de herramientas
row_tools.addWidget(btn_left)
row_tools.addWidget(btn_right)
row_tools.addWidget(btn_flip)
row_tools.addWidget(btn_sharp)
row_tools.addWidget(btn_bw)
col2.addLayout(row_tools)    # Insertar la barra al fondo de la columna 2

row.addLayout(col1, 20)      # Columna de archivos toma el 20% del ancho total
row.addLayout(col2, 80)      # Columna de edición toma el 80% del ancho total
win.setLayout(row)

win.show()

# Variable global para almacenar la ruta de la carpeta seleccionada
workdir = ''

# === 2. LOGÍSITICA DE ARCHIVOS Y FILTRADO ===

def filter(files, extensions):
   '''Filtra una lista de archivos y devuelve solo aquellos con extensiones de imagen válidas'''
   result = []
   for filename in files:
       for ext in extensions:
           if filename.endswith(ext):
               result.append(filename)
   return result

def chooseWorkdir():
   '''Abre el explorador de archivos nativo para seleccionar un directorio de trabajo'''
   global workdir
   workdir = QFileDialog.getExistingDirectory()

def showFilenamesList():
   '''Controlador del botón Carpeta: Selecciona, filtra y llena la lista visual (QListWidget)'''
   extensions = ['.jpg','.jpeg', '.png', '.gif', '.bmp']
   chooseWorkdir()
   if workdir: # Asegura que el usuario no haya cerrado el diálogo sin elegir nada
       filenames = filter(os.listdir(workdir), extensions)
       lw_files.clear()
       for filename in filenames:
           lw_files.addItem(filename)

# Evento: Al hacer clic en "Carpeta", se lee el directorio
btn_dir.clicked.connect(showFilenamesList)


# === 3. CLASE MAESTRA DE PROCESAMIENTO (MÓDULO DE EDICIÓN) ===
class ImageProcessor():
   def __init__(self):
       self.image = None
       self.dir = None
       self.filename = None
       self.save_dir = "Modificado/" # Subcarpeta para no dañar las fotos originales

   def loadImage(self, filename):
       '''Carga la imagen seleccionada desde el disco duro a la memoria usando Pillow'''
       self.filename = filename
       fullname = os.path.join(workdir, filename)
       self.image = Image.open(fullname)

   def saveImage(self):
       '''Guarda de forma segura una copia de la imagen editada en la subcarpeta 'Modificado/\''''
       path = os.path.join(workdir, self.save_dir)
       if not(os.path.exists(path) or os.path.isdir(path)):
           os.mkdir(path) # Crea la carpeta si no existía previamente
       fullname = os.path.join(path, self.filename)
       self.image.save(fullname)

   # --- MÉTODOS DE EDICIÓN DE IMAGEN ---

   def do_bw(self):
       '''Transformación 1: Convierte la imagen a escala de grises ("L" = Luminancia)'''
       if self.image:
           self.image = self.image.convert("L")
           self.saveImage()
           image_path = os.path.join(workdir, self.save_dir, self.filename)
           self.showImage(image_path)

   def do_left(self):
       '''Transformación 2: Rota la imagen 90 grados a la izquierda (Antihorario)'''
       if self.image:
           self.image = self.image.transpose(Image.ROTATE_90)
           self.saveImage()
           image_path = os.path.join(workdir, self.save_dir, self.filename)
           self.showImage(image_path)

   def do_right(self):
       '''Transformación 3: Rota la imagen 270 grados a la izquierda (Equivale a 90° horario)'''
       if self.image:
           self.image = self.image.transpose(Image.ROTATE_270)
           self.saveImage()
           image_path = os.path.join(workdir, self.save_dir, self.filename)
           self.showImage(image_path)

   def do_flip(self):
       '''Transformación 4: Reflejo horizontal (Efecto espejo de izquierda a derecha)'''
       if self.image:
           self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
           self.saveImage()
           image_path = os.path.join(workdir, self.save_dir, self.filename)
           self.showImage(image_path)

   def do_sharpen(self):
       '''Transformación 5: Aplica un filtro de enfoque/nitidez usando ImageFilter de Pillow'''
       if self.image:
           self.image = self.image.filter(SHARPEN)
           self.saveImage()
           image_path = os.path.join(workdir, self.save_dir, self.filename)
           self.showImage(image_path)

   def showImage(self, path):
       '''Reescala la imagen de manera proporcional y la dibuja en el contenedor de la pantalla'''
       lb_image.hide()
       pixmapimage = QPixmap(path)
       w, h = lb_image.width(), lb_image.height()
       pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio) # Mantiene el aspecto original
       lb_image.setPixmap(pixmapimage)
       lb_image.show()

# === 4. CONTROL DE EVENTOS DINÁMICOS ===

def showChosenImage():
   '''Se activa automáticamente al hacer clic sobre cualquier archivo de la lista visual'''
   if lw_files.currentRow() >= 0:
       filename = lw_files.currentItem().text()
       workimage.loadImage(filename)
       # Muestra la imagen original (recién cargada)
       workimage.showImage(os.path.join(workdir, workimage.filename))

# Instancia global encargada de gestionar los cambios del archivo actual
workimage = ImageProcessor() 

# Escucha si el usuario hace clic en un elemento diferente de la lista
lw_files.currentRowChanged.connect(showChosenImage)

# Conexión final de toda la botonera de edición a sus respectivos métodos lógicos
btn_bw.clicked.connect(workimage.do_bw)
btn_left.clicked.connect(workimage.do_left)
btn_right.clicked.connect(workimage.do_right)
btn_sharp.clicked.connect(workimage.do_sharpen)
btn_flip.clicked.connect(workimage.do_flip)

# Arranca el bucle de eventos para mantener la aplicación corriendo
app.exec()