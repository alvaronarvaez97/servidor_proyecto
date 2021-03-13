from datetime import datetime
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
import time
import paho.mqtt.client as mqtt
import time
from datetime import datetime


class analitica():
    ventana = 10
    pronostico = 3
    file_name = "data_base.csv"
    servidor = "rabbit"

    def __init__(self) -> None:
        self.load_data()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.servidor, 1883, 60)
        self.client.loop_start()

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("$SYS/#")

    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def load_data(self):

        if not os.path.isfile(self.file_name):
            self.df = pd.DataFrame(columns=["fecha", "sensor", "valor"])
        else:
            self.df = pd.read_csv (self.file_name)

    def update_data(self, msj):
        msj_vetor = msj.split(",")
        new_data = {"fecha": msj_vetor[0], "sensor": msj_vetor[1], "valor": float(msj_vetor[2])}
        self.df = self.df.append(new_data, ignore_index=True)
        self.analitica_descriptiva()
        self.analitica_predictiva()
        self.guardar()

    def print_data(self):
        print(self.df)

    def analitica_descriptiva(self):
        self.operaciones("temperatura")
        self.operaciones("densidad")

    def operaciones(self, sensor):
        df_filtrado = self.df[self.df["sensor"] == sensor]
        df_filtrado = df_filtrado["valor"]
        df_filtrado = df_filtrado.tail(self.ventana)
        now = datetime.now()
        date_time = now.strftime('%d.%m.%Y %H:%M:%S')
        self.client.publish("descriptiva/max-{}".format(sensor), "{},{},{}".format(date_time,sensor,df_filtrado.max(skipna = True)))
        self.client.publish("descriptiva/min-{}".format(sensor), "{},{},{}".format(date_time,sensor,df_filtrado.min(skipna = True)))
        self.client.publish("descriptiva/mean-{}".format(sensor), "{},{},{}".format(date_time,sensor,df_filtrado.mean(skipna = True)))
        self.client.publish("descriptiva/median-{}".format(sensor), "{},{},{}".format(date_time,sensor,df_filtrado.median(skipna = True)))
        self.client.publish("descriptiva/std-{}".format(sensor), "{},{},{}".format(date_time,sensor,df_filtrado.std(skipna = True)))

    def analitica_predictiva(self):
        self.regresion("temperatura")
        self.regresion("densidad")

    def regresion(self, sensor):
        df_filtrado = self.df[self.df["sensor"] == sensor]
        df_filtrado = df_filtrado.tail(self.ventana)
        df_filtrado['fecha'] = pd.to_datetime(df_filtrado.pop('fecha'), format='%d.%m.%Y %H:%M:%S')
        df_filtrado['segundos'] = [time.mktime(t.timetuple()) - 18000 for t in df_filtrado['fecha']]
        tiempo = df_filtrado['segundos'].std(skipna = True)
        if np.isnan(tiempo):
            return
        tiempo = int(round(tiempo))
        ultimo_tiempo = df_filtrado['segundos'].iloc[-1]
        ultimo_tiempo = ultimo_tiempo.astype(int)
        range(ultimo_tiempo + tiempo,(self.pronostico + 1) * tiempo + ultimo_tiempo, tiempo)
        nuevos_tiempos = np.array(range(ultimo_tiempo + tiempo,(self.pronostico + 1) * tiempo + ultimo_tiempo, tiempo))

        X = df_filtrado["segundos"].to_numpy().reshape(-1, 1)  
        Y = df_filtrado["valor"].to_numpy().reshape(-1, 1)  
        linear_regressor = LinearRegression()
        linear_regressor.fit(X, Y)
        Y_pred = linear_regressor.predict(nuevos_tiempos.reshape(-1, 1))
        for tiempo, prediccion in zip(nuevos_tiempos, Y_pred):
            time_format = datetime.utcfromtimestamp(tiempo)
            date_time = time_format.strftime('%d.%m.%Y %H:%M:%S')
            self.client.publish("predictiva/{}".format(sensor), "{},{},{}".format(date_time,sensor,prediccion[0]))

    def guardar(self):
        self.df.to_csv(self.file_name, encoding='utf-8')
