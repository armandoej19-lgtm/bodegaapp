# Guía de Usuario - Bodega Register App

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Uso Básico](#uso-básico)
4. [Funcionalidades Avanzadas](#funcionalidades-avanzadas)
5. [Solución de Problemas](#solución-de-problemas)

## 🎯 Introducción

Bodega Register App es una aplicación para gestionar el inventario de dispositivos electrónicos. Permite registrar, buscar, modificar y exportar información sobre dispositivos en bodega.

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- 100 MB de espacio libre
- Permisos de administrador (para instalación)

### Pasos de Instalación
1. Descomprimir el archivo de instalación
2. Ejecutar `install.bat` (Windows) o `install.sh` (Linux/Mac)
3. Seguir las instrucciones en pantalla

## 💻 Uso Básico

### 1. Registrar un Nuevo Dispositivo
1. Abrir la aplicación
2. Ir a la pestaña "Registro"
3. Hacer clic en "(+) Añade un nuevo dispositivo"
4. Completar todos los campos obligatorios (*)
5. Hacer clic en "Guardar"

**Campos Obligatorios:**
- Número de Serie
- Tipo de Dispositivo
- Modelo

### 2. Buscar Dispositivos
1. Ir a la pestaña "Búsqueda"
2. Ingresar término de búsqueda
3. Seleccionar criterio de búsqueda
4. Hacer clic en "Buscar"

**Criterios de Búsqueda Disponibles:**
- Por Serial (número de serie)
- Por Tipo (laptop, desktop, etc.)
- Por Modelo
- Por Fecha
- Todos (muestra todos los dispositivos)

## 🔧 Funcionalidades Avanzadas

### Exportación de Datos
La aplicación permite exportar datos en dos formatos:

#### Exportar a Excel
1. Realizar una búsqueda
2. Hacer clic en "Exportar .xlsx"
3. Seleccionar opción:
   - **Todos los datos**: Exporta toda la base de datos
   - **Datos filtrados**: Exporta solo los resultados de la búsqueda actual
4. Elegir ubicación y nombre del archivo

### Eliminación de Registros
**Precaución**: La eliminación es permanente

#### Eliminar Registro Individual
1. Seleccionar el registro en la tabla
2. Hacer clic en "Eliminar Seleccionado"
3. Confirmar la eliminación

#### Eliminar Múltiples Registros
1. Realizar una búsqueda específica
2. Hacer clic en "Eliminar Filtrados"
3. Confirmar la eliminación

**Restricciones:**
- No se pueden eliminar todos los dispositivos a la vez
- No se pueden eliminar todos los dispositivos de un tipo

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. "Error al conectar a la base de datos"
- Verificar que el archivo `bodega.db` existe en la carpeta `data/`
- Comprobar permisos de escritura en la carpeta

#### 2. "Serial ya existe"
- Cada número de serie debe ser único
- Verificar si el dispositivo ya está registrado

#### 3. "Error al exportar a Excel"
- Verificar que Excel no esté abierto con el archivo
- Comprobar espacio en disco
- Asegurarse de tener permisos de escritura

### Contacto y Soporte
Para reportar problemas o solicitar ayuda:
- Email: soporte@bodega-app.com
- Teléfono: +1 800-BODEGA-APP

## 📊 Estructura de Datos

### Tabla DeviceReg
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Identificador único |
| serialno | TEXT | Número de serie (único) |
| type | VARCHAR(60) | Tipo de dispositivo |
| model | TEXT | Modelo del dispositivo |
| failuretype | VARCHAR(60) | Tipo de falla |
| entry_date | TIMESTAMP | Fecha de registro |
| observations | TEXT | Observaciones adicionales |

### Códigos de Falla
- [0] Sin fallas
- [1] Falla de Hardware
- [2] Falla Crítica de Hardware
- [3] Falla de Software
- [4] Falla Crítica de Software

## ⚙️ Configuración

### Tipos de Dispositivo Predefinidos
La aplicación incluye los siguientes tipos:
- Laptop
- Desktop
- Tablet
- Teléfono Inteligente
- Server
- Switch
- Punto de Acceso
- Impresora
- Cámara
- Altavoz
- Monitor
- Other

### Personalización
Para agregar nuevos tipos o modelos, contactar al administrador del sistema.