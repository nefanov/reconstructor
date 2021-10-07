from simulator import *
from threading import Thread


def start():
    API = SysAPI()
    return API


def run_sim_instances(config={'instances':[{'func':lambda :start()}], 'tpool':[]}):
    for item in config['instances']:
        config['tpool'].append(Thread(target = item['func']))
        config['tpool'][-1].start()

    for i, thread in enumerate(config['tpool']):
        thread.join()
        print("End of thread:", thread)

    print("Simulation is finished")
    return

if __name__ == '__main__':
    run_sim_instances()
