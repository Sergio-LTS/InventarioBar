# 🍹 InventarioBar 

**Autor:** Sergio Zuñiga  
**Universidad:** Universidad Católica de Colombia  
**Programa:** Ingeniería de Sistemas y Computación  
**Versión:** ProMax  
**Framework:** FastAPI + SQLAlchemy (async)  
**Base de datos:** PostgreSQL (Render) + supabase

---

## Tabla de contenidos

* [Descripción general](#descripción-general)
* [Objetivos del proyecto](#objetivos-del-proyecto)
* [Tecnologías utilizadas](#tecnologías-utilizadas)
* [Modelado de datos](#modelado-de-datos)
  * [Usuario](#usuario)
  * [Producto](#producto)
  * [Venta](#venta)
  * [InventarioMovimiento](#inventariomovimiento)
  * [Tablas de resumen (Dashboard)](#tablas-de-resumen-dashboard)
  * [Relaciones (ERD)](#relaciones-erd)
* [Instalación y ejecución](#instalación-y-ejecución)
* [Mapa de endpoints](#mapa-de-endpoints)
  * [Web (Jinja)](#web-jinja)
  * [API (JSON)](#api-json)
* [Reglas de negocio](#reglas-de-negocio)
* [Control de versiones (Git y GitHub)](#control-de-versiones-git-y-github)

---

## Descripción general

**InventarioBar** es un backend asíncrono con **FastAPI + SQLAlchemy 2.0 async** que gestiona **Usuarios, Productos y Ventas**, mantiene el **inventario** mediante **movimientos automáticos** (entradas/salidas) y ofrece un **Dashboard** con productos más/menos vendidos y un **resumen de ventas** (monto, unidades, ticket promedio).  
Incluye vistas HTML con **Jinja2** y carga opcional de imágenes a **Supabase Storage**.

---

## Objetivos del proyecto

**Objetivo general**  
Construir un sistema de inventario y ventas para un bar con operaciones **CRUD**, control de stock y un **dashboard** de desempeño.

**Objetivos específicos**
* Registrar y administrar **usuarios**, **productos** y **ventas**.
* Actualizar inventario mediante **movimientos** automáticos en cada venta.
* Calcular **Top/Bottom** de productos vendidos y **resúmenes** del periodo.
* Exponer endpoints HTML (Jinja) y **API REST** (JSON).
* Preparar el proyecto para **despliegue en Render** con PostgreSQL gestionado.

---

## Tecnologías utilizadas

| Tecnología      | Descripción                                                    |
|-----------------|----------------------------------------------------------------|
| FastAPI         | Framework ASGI para construir APIs rápidas                      |
| SQLAlchemy 2.0  | ORM con **async** (AsyncSession)                                |
| PostgreSQL      | Base de datos principal (Render o local)                        |
| Uvicorn         | Servidor ASGI                                                   |
| Pydantic v2     | Validación de datos/esquemas                                    |
| Jinja2          | Templates HTML para vistas web                                  |
| Supabase        | (Opcional) Storage para imágenes                                |
| Python 3.12+    | Lenguaje de programación                                        |

---

## Modelado de datos

### Usuario

| Atributo        | Tipo  | Descripción                          |
|-----------------|-------|--------------------------------------|
| `id_usuario`    | int   | PK autoincremental                   |
| `nombre_usuario`| str   | Nombre para mostrar                  |
| `correo`        | str   | Email único                          |
| `rol`           | str   | Rol (admin/operador, etc.)           |
| `foto_url`      | str   | URL a imagen (opcional)              |

### Producto

| Atributo        | Tipo   | Descripción                           |
|-----------------|--------|---------------------------------------|
| `id_producto`   | int    | PK autoincremental                    |
| `nombre`        | str    | Nombre del producto                   |
| `categoria`     | str    | Categoría (ej. bebidas, snacks)       |
| `marca`         | str    | Marca                                 |
| `cantidad`      | int    | Stock actual (≥ 0)                    |
| `precio_venta`  | float  | Precio de venta                       |
| `imagen_url`    | str    | URL a imagen (opcional)               |

### Venta

| Atributo           | Tipo  | Descripción                             |
|--------------------|-------|-----------------------------------------|
| `id_venta`         | int   | PK autoincremental                      |
| `id_usuario`       | int   | FK → Usuario                            |
| `id_producto`      | int   | FK → Producto                           |
| `cantidad_vendida` | int   | Unidades vendidas (> 0)                 |
| `fecha_venta`      | dt    | Fecha/hora de la venta                  |

### InventarioMovimiento

| Atributo          | Tipo  | Descripción                                        |
|-------------------|-------|----------------------------------------------------|
| `id_movimiento`   | int   | PK autoincremental                                 |
| `id_producto`     | int   | FK → Producto                                      |
| `tipo_movimiento` | str   | `entrada` / `salida`                               |
| `cantidad`        | int   | Unidades afectadas (> 0)                           |
| `descripcion`     | str   | Motivo (p.ej. "venta", "ajuste")                   |
| `fecha`           | dt    | Fecha/hora del movimiento                          |

### Tablas de resumen (Dashboard)

| Tabla                        | Campos clave                           | Uso                                   |
|-----------------------------|----------------------------------------|----------------------------------------|
| `productos_mas_vendidos`    | `id_producto`, `total_vendido`         | Top vendidos                           |
| `productos_menos_vendidos`  | `id_producto`, `total_vendido`         | Menos vendidos                         |
| **Resumen de ventas (consulta/agg)** | `monto_total`, `unidades_vendidas`, `ticket_promedio` | KPIs del periodo (desde/hasta) |

> Notas:  
> * Los resúmenes admiten reconstrucción desde el botón **Rebuild** del Dashboard.  
> * Las FKs en tablas de resumen están en **ON DELETE CASCADE** para evitar conflictos al eliminar productos.

### Relaciones (ERD)

```mermaid
erDiagram
    USUARIO {
        int id_usuario PK
        string nombre_usuario
        string correo
        string rol
        string foto_url
    }

    PRODUCTO {
        int id_producto PK
        string nombre
        string categoria
        string marca
        int cantidad
        float precio_venta
        string imagen_url
    }

    VENTA {
        int id_venta PK
        int id_usuario FK
        int id_producto FK
        int cantidad_vendida
        datetime fecha_venta
    }

    INVENTARIO_MOVIMIENTO {
        int id_movimiento PK
        int id_producto FK
        string tipo_movimiento
        int cantidad
        string descripcion
        datetime fecha
    }

    PRODUCTOS_MAS_VENDIDOS {
        int id_producto FK
        int total_vendido
    }

    PRODUCTOS_MENOS_VENDIDOS {
        int id_producto FK
        int total_vendido
    }

    USUARIO ||--o{ VENTA : realiza
    PRODUCTO ||--o{ VENTA : se_vende_en
    PRODUCTO ||--o{ INVENTARIO_MOVIMIENTO : genera
    PRODUCTO ||--o{ PRODUCTOS_MAS_VENDIDOS : resume
    PRODUCTO ||--o{ PRODUCTOS_MENOS_VENDIDOS : resume
