import datetime
import pandas as pd
import numpy as np

def update(file_name):
    datos_pandas = leer_datos(file_name)
    funcion_maximo(datos_pandas)
    """
    Inserte aqui las otras funciones.
    funcion_Minimo()
    funcion_Mediana()
    funcion_Promedio()
    funcion_Desviacion()
    funcion_Varianza()
    """
    datos_graficar = leer_datos(file_name)
    return datos_graficar


def funcion_maximo(datos):
    """
    Inserte aqui la operacíon para calcular el max.
    borrar pass
    """
    pass


def leer_datos(file_name):
    datos_pandas = pd.read_csv(file_name, index_col=0, parse_dates=True)
    return datos_pandas