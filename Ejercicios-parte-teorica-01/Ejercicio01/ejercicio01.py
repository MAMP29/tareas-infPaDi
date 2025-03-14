from math import remainder
from threading import Thread
from multiprocessing import Process
from time import time, sleep
import random


def task_creator(n=12, min_time=1, max_time=40):
    vector = []
    for _ in range(n):
        vector.append(
            lambda min_t=min_time, max_t=max_time :
            sleep(random.randint(min_t,max_t))
        ) # Almacena la función directamente mediante esta función anonima

    return vector

def workers_number_creator(n=12):
    return [1, 2, n//4, n//2, n]


def execute_per_threads(tasks, workers_to_use, threads):
    times = []
    total_start_time = time()
    for max_workers in workers_to_use:

        print(f"Empezando con el worker {max_workers}")

        if max_workers==1:
            t1 = time()
            execute_tasks(tasks)
            t2 = time()
            elapse_time = t2 - t1
            times.append((max_workers, elapse_time))
            print(f"Tiempo total de calculo {elapse_time}")
            continue


        workers = []
        chunk_size = len(tasks) // max_workers
        left = len(tasks) % max_workers

        start = 0
        for t in range(max_workers):
            end = start + chunk_size + (1 if t < left else 0)

            if threads:
                worker = Thread(target=execute_tasks, args=(tasks[start:end],))
                worker.daemon = True
            else:
                worker = Process(target=execute_tasks, args=(tasks[start:end],))

            workers.append(worker)
            start = end

        t1 = time()

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        t2 = time()
        elapse_time = t2 - t1
        times.append((max_workers,elapse_time))

        print(f"Tiempo total de calculo para {max_workers} workers: {elapse_time}")

    total_end_time = time()
    total_time = total_end_time - total_start_time
    times.append(("total time", total_time))
    print(f"Tiempo total para todo el proceso: {total_time}")

    return times


def execute_tasks(tasks):
    for task in tasks:
        task()

tasks_vector = [ # Funciones anónimas para despues
    lambda: sleep(20),
    lambda: sleep(5),
    lambda: sleep(10),
    lambda: sleep(30),
    lambda: sleep(12),
    lambda: sleep(8),
    lambda: sleep(15),
    lambda: sleep(10),
    lambda: sleep(20),
    lambda: sleep(11),
    lambda: sleep(25),
    lambda: sleep(35),
]


worker_vector = workers_number_creator(len(tasks_vector))

print(len(tasks_vector))
print(worker_vector)

final_times = execute_per_threads(tasks_vector, worker_vector, False)


for f in final_times:
    print(f)
