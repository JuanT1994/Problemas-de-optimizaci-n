import cplex
import sys
import matplotlib.pyplot as plt

TOLERANCE =10e-6 

################## Clase para datos inst #################

class DietData:
    def __init__(self):
        # init carga la instancia por default de la clase.
        self.n = 0 
        self.m = 0
        self.cost = []
        # informacion relacionada a nutrientes.
        self.nutr = {}
        self.reqs = {}
        self.perc = 0
        self.req_names = []

    def get_contrib(self,x,key):
        ret = 0
        for i in range(len(x)):
            ret += x[i]*self.nutr[key][i]
        return ret

    def load(self, filename):
        f = open(filename)
        
        # datos generales
        line = f.readline().split(' ')
        self.n = int(line[0])

        self.m = int(line[1])

        # Leemos los costos
        line = f.readline().split(' ')
        print(line)
        self.cost = [float(i) for i in line]

        # Leemos los nutrientes restantes
        for i in range(self.m):
            line = f.readline().split(' ')
            self.req_names.append(line[0])
            self.reqs[line[0]] = float(line[1])
            self.nutr[line[0]] = [float(k) for k in line[2:]]
    
    def _data_check(self):
        pass

    def __repr__(self):
        ret = ''
        ret += 'n = %d\nm = %d\nperc = %d\n' % (self.n,self.m,self.perc)
        ret += 'cost: %s\n' % (','.join([str(x) for x in self.cost]))
        ret += 'nutr:\n'
        for k in self.nutr:
            ret += '\t%s: %s\n' % (k,','.join([str(x) for x in self.nutr[k]]))
        ret += 'reqs. nutr.:\n'
        for k in self.reqs:
            ret += '\t%s: %d\n' % (k,self.reqs[k])

        return ret

################## Funciones auxiliares ##################

def get_instance_data(filename):
    #Funcion que encapsula la obtencion de la informacion de la instancia.
    #Retorna una instancia de la clase DietData

    data = DietData()
    data.load(filename)

    return data

def add_constraint_matrix(myprob, data,k):
    #Completamos la funcion que agrega la matriz de restricciones donde:
    # data.nutr[j] contiene el apoporte de cada alimiento para el nutriente j
    # data.ref[j] contiene el valor b_j para el nutriente j
    #Generamos una iteración que recorre los diferentes nutrientes y agrega las restricciones:
    ind = list(range(data.n))
    for j in data.nutr:
        val = data.nutr[j]
        row = [ind,val]
        myprob.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[data.reqs[j]*(1-k)])
        myprob.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[data.reqs[j]*(1+k)])
        


def populate_by_row(myprob,data,k):
    
    #Agregamos las variables, definimos la función objetivo y las cotas inferiores
    myprob.variables.add(obj = data.cost, lb = [0]*data.n)
    myprob.objective.set_sense(myprob.objective.sense.minimize)
    #Llamamos a la función add_constraint_matrix 
    add_constraint_matrix(myprob, data,k)

    #Generamos el archivo test_dieta_tp1 en caso de necesitar debbugear el código
    myprob.write('test_dieta_tp1.lp')

def solve_lp(myprob):
    #Resolvemos el modelo, para una instancia y un k particular, y obtieneos 
    #los resultados, devolviendo aquellos que sean necesarios para realizar el analisis
    myprob.solve()
    
    f_obj=myprob.solution.get_objective_value()
    x=myprob.solution.get_values()
    
    return f_obj,x

def plot_two_series(x,y,z,name_y = '',name_z = ''):
    #Esta función viene dada en el trabajo práctico. 
    #Toma tres listas de igual longitud x,y,z y grafica las dos series (x,y) e (x,z)
    #Los strings adicionales sirven para asignar un nombre a cada serie 
    #y que figuren en la leyenda del grafico
    
    fig = plt.figure()
    ax = fig.add_subplot(111)

    lns1 = ax.plot(x, y, 'x-', color="blue", label = name_y)
    lns2 = ax.plot(x, z, 'o-', color="green", label = name_z)
    ax2 = ax.twinx()


    #Added these three lines
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)

    fig.tight_layout()
    
    plt.show()

################## Definimos el Main ##################

def main(filename):

    # Utilizamos la función get_instnce_data para inicializar la instancia de DietData
    data= get_instance_data(filename)
    #print(data)
    
    #Para cada valor de k resolvemos el modelo
    perc=[]
    i=0
    soln=[]
    for i in range(0,20):
        perc.append(0.01*(i+1))
    
    for k in perc:
        myprob= cplex.Cplex()
        populate_by_row(myprob,data,k)
        soln.append(solve_lp(myprob))
    #for i in soln:
        #print(i[1])


    
    #Graficamos los resultados resultados, para ello armamos 4 listas con los datos de los costos,
    #los aportes de calorías, proteínas y calcio en cada solución del modelo para cada instancia k
    
    #nutrientes=["calorias","proteinas","calcio"]
    #data_nutr=[]*len(nutrientes)
    #for j in nutrientes:
    #print(perc)
    #Generamos la lista de los costos:
    data_cost=[]
    
    for i in soln:
        data_cost.append(i[0])
    #print(data_cost)
    
    #Generamos las listas de proteínas, calorías y calcio, para ello llamamos a la función "get_contrib"
    data_prot=[]
    data_kal=[]
    data_calcio=[]    
    for i in soln:
        data_prot.append(data.get_contrib(i[1],"proteinas"))
        data_kal.append(data.get_contrib(i[1],"calorias"))
        data_calcio.append(data.get_contrib(i[1],"calcio"))
    
    #print(data_prot)
    #print(data_kal)
    #print(data_calcio)
    
    #Generamos 4 gráficos, para ello llamamos a la función "plot_two_series":
    #1:Costos vs. k
    plt.plot(perc,data_cost, marker='x', color="blue")
    #2:Costos, Proteínas vs. k      
    plot_two_series(perc,data_cost,data_prot,name_y = 'Costo',name_z = 'Proteinas')        
    #3:Costos, Calcio vs. k    
    plot_two_series(perc,data_cost,data_calcio,name_y = 'Costo',name_z = 'Calcio') 
    #4:Costos, Calorías vs. k    
    plot_two_series(perc,data_cost,data_kal,name_y = 'Costo',name_z = 'Calorias')

if __name__ == "__main__":
    main(sys.argv[1])
