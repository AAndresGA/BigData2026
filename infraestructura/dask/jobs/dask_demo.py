from dask.distributed import Client
import time

# conectar al cluster (nombre de servicio en Docker Compose)
client = Client("tcp://dask-scheduler:8786")

def tarea(x):
    time.sleep(2)  # simula trabajo pesado
    return x * x

# enviar tareas en paralelo
futures = client.map(tarea, range(10))

# obtener resultados
resultados = client.gather(futures)

print(resultados)
