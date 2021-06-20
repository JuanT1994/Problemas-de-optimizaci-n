import numpy as np
import matplotlib.pyplot as plt
from PickersData import PickersData
import random
import statistics

##### Funciones Dadas #####
def get_pdf(data):
    #Dado un vector con muestras de una variable, retorna dos listas con los valores (a intervalos de 1) y su correspondiente frecuencia de ocurrencia
    bins = range(1,int(max(data) + 2))
    count, bin_edges=np.histogram(data, bins=bins)
    probs = count/sum(count)
    
    return bin_edges[:-1],probs

def get_cdf(probs):
    #Dado un vector con probabilidades (pdf), retorna un vector de la misma dimension con la cdf. Probs puede ser la lista probs que retorna get_pdf.
    return np.cumsum(probs)

def get_picker(pickers_stat):
    #Dada una lista con el tiempo en que cada picker termina su orden actual, devuelve el indice (i.e., picker) que termina primero
    return pickers_stat.index(min(pickers_stat))

def analyze_results(total_times,total_revs):
    #Fucion que concentra el analisis de los resultados para un determinado escenario y con una cantidad de pickers dada.
    
    print('Completados en 60 mins:',get_prob_completed(total_times,3600))
    print('Tiempo promedio:',statistics.mean(total_times))
    print('Rev. promedio:',statistics.mean(total_revs))
    
    # Convertimos a minutos para agrupar.
    total_times_mins = [int(i/60.0) for i in total_times]
    b = range(max(total_times_mins) + 1)
    # Cuando querramos graficar, descomentamos.
    plt.hist(total_times_mins, bins = b, density=True) 
    plt.show() 
    plt.hist(total_times_mins, bins = b, density=True, cumulative=True) 
    plt.show()
    
def get_prob_completed(times, value):
    success = [t for t in times if t <= value]
    return len(success)/len(times)

######################################################################################
    
def simulate_uniform(a,b):
    c = a + (b-a)*random.random()
    return int(c)
    

def simulate_empirical(vals, cumprobs):
    
    #Genera un numero aleatorio en base a una distribucion empirica usando el metodo de la transformada inversa.
    
    r=random.random()
    i=0 #va a actuar de contador
    while cumprobs[i]<=r:
        if i<len(cumprobs)-1:
            i=i+1
        else:
            i=len(cumprobs)-1
    
    return vals[i]
        
def generate_orders(n_orders, items_vals, items_cumprobs):
    
    #Simula la cantidad de itmes que tendra cada orden. La idea es usar la funcion simulate_empirical. Para eso, recibe: 
    
    ordenes=[]*n_orders #Lista que guarda los ítems de cada orden
 
    for i in range(0,n_orders):
        ordenes.append(simulate_empirical(items_vals,items_cumprobs)) #se ingresa in int a la lista correspondiente al número de ítems de esa orden
        
    return ordenes

def simulate_order_time(n_items, picker, pickers_dist):
    
    #Simulamos el tiempo que le lleva a un picker procesar una determinada orden. Recordar que una orden esta definida por el numero de items
	#que tiene, y que cada picker tiene su propia distribucion de tiempos de inter-picks.
	
    time_tot_to_process=0 #variable que va a acumular el tiempo que tarda en procesar la orden sumando los tiempos entre cada item que la componen
    
    for i in range (0,n_items):
        j=simulate_empirical(pickers_dist[picker]['times'], pickers_dist[picker]['cumprobs'])
        time_tot_to_process = time_tot_to_process + j #se acumulan los tiempos de cada item
    return time_tot_to_process

def process_orders(orders, pickers_dist, n_pickers):
    
    #pickers_dist es un parámetro que hay que pasarle a la función simulte_orders_time
    
    pickers_stat = [0.0]*n_pickers
    collected_rev = 0.0
    
    for order in orders:
        free_picker = get_picker(pickers_stat)
        tiempo_de_procesamiento = simulate_order_time(order, free_picker, pickers_dist)
        pickers_stat[free_picker] = pickers_stat[free_picker] + tiempo_de_procesamiento
        if tiempo_de_procesamiento <= 3600:
            collected_rev = collected_rev + 100
    
    last_to_finish = max(pickers_stat)
    return last_to_finish, collected_rev

def simulate_process(pickers_data, outcome, number_pickers, n_sims):
        
    items_vals, items_probs = get_pdf(pickers_data.items_per_order) 
    items_cumprobs = get_cdf(items_probs) 
    
    pickers_dist = {}
    
    for picker in pickers_data.picker_times:
        times, probs = get_pdf(pickers_data.picker_times[picker])
        cumprobs = get_cdf(probs)
        pickers_dist[picker] = {'times': times, 'cumprobs': cumprobs}
        
    total_times = []
    total_revs = []
    
    for i in range(n_sims):
        
        cant_orders = simulate_uniform(outcome[0],outcome[1])
        ordenes = generate_orders(cant_orders, items_vals, items_cumprobs) #se genera un alista de int, donde cada número representa los ítems que componen la orden
        
        tiempos,revenues=process_orders(ordenes, pickers_dist, number_pickers) #devuelve dos valores, uno con el tiempo que se tardo en procesar todos los pedidos y el revenue generado.
        total_times.append(tiempos)
        total_revs.append(revenues)
        
    return total_times,total_revs #retorna una lista con el tiempo que tardó en procesar todas las órdenes y el revenue generado
        
        
def main():
    
    random.seed(0)
    
    max_number_pickers = 10 # No tocar este valor. 
    number_of_simulations = 1000
    
    # Definicion de los posibles escenarios como una lista de tuplas, donde cada tupla representa los valores Unif(a,b)
	# Impacto bajo: Unif(20,25), posicion 0 de la lista scenarios.
	# Impacto moderado: Unif(30,40), posicion 1 de la lista scenarios.
	# Impacto alto: Unif(45,60), posicion 2 de la lista scenarios.
    
    scenarios = [(20,25),(30,40),(45,60)]
    
    # Se leen los datos de archivo y se procesan. No deberian modificar esto. Es algo simple de hacer (pero molesto!)
    data = PickersData(max_number_pickers)
    
    for outcome in scenarios:
        
        # Para cada escenario, el posible numero de pickers.
        
        print("Escenario con demanda uniforme: " + str(outcome))
       
        for n_pickers in range(5,max_number_pickers + 1):
            
            print("Cantidad de pickers: " + str(n_pickers))
            
            times,revs = simulate_process(data, outcome, n_pickers, number_of_simulations)
            
            analyze_results(times,revs)
            
    ### Posibilidad 2: realizar una ejecucion por cada combinacion cambiando las opciones de outcome y n_pickers.
	### Descomentar las siguientes lineas, e ir modificando el valor de las variables outcome y n_pickers.
	# outcome = outcomes[0] 
	# n_pickers = 6
	## Para cada posible escenario y numero de pickers realizamos las number_of_simulations simulaciones.
	#times,revs = simulate_process(data, outcome, n_pickers, number_of_simulations)
	## Procesamos los resultados
	#analyze_results(times,revs)


if __name__ == '__main__':
    main()
    
            
    
    
    
            
        
        
        
    
    
    
    

    
    




















































    