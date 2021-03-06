import matplotlib.pyplot as plt
import numpy as np

from joint_data.joint_pos_recorder import JointPosLoader
import pickle
from GaitAnaylsisToolkit.LearningTools.Runner import TPGMMRunner
from GaitAnaylsisToolkit.LearningTools.Trainer import TPGMMTrainer
import numpy.polynomial.polynomial as poly
import pulp


def temp_test():

    data = read_data()[0]
    resampled = resample(data)
    t = np.linspace(0, 1, len(data)  )
    plt.plot(t, data  )
    t = np.linspace(0, 1, len(resampled))
    plt.plot(t, resampled)
    plt.show()


def read_data():

    demos = {}
    for i in range(6):
        demos[i] = []


    for file in [1,2,3,4,5]:
        # m, l = JointPosLoader.load_by_prefix(prefix='JP#2021-06-28 13', folder_path='./joint_data/'+str(file))
        m, l = JointPosLoader.load_by_prefix(prefix='JP#2021-08-17 13', folder_path='./joint_data2/'+str(file))
        demo = {}

        for i in range(6):
            demo[i] = []
        for i in range(len(m)):
            for j in range(len(m[0])):
                pos = m[i][j]['pos']
                for k in range(len(pos)):
                    demo[k].append(pos[k])
        for key, value in demo.items():
            demos[key].append( smooth(demo[key]) )

    return demos


def smooth(x):
    N=10
    return np.convolve(x, np.ones(N)/N, mode='valid')

def resample(data):

    t = np.linspace(0, 1, len(data))
    coefs = poly.polyfit( t , data, 3)
    ffit = poly.Polynomial(coefs)  # instead of np.poly1d
    t = np.linspace(0,1,100)
    y_fit = ffit(t)
    return y_fit

def plot_raw(my_data,runner_file=None):

    f, ax = plt.subplots(6)

    for ii, traj in enumerate([my_data[0], my_data[1],my_data[2],my_data[3],my_data[4],my_data[5]]):
        for demo in traj:
            ax[ii].plot(smooth(demo), '-')



    if runner_file is not None:
        runner = TPGMMRunner.TPGMMRunner(runner_file)
        path = runner.run()
        for i in range(6):
            ax[i].plot(path[:, i], linewidth=4)

    plt.show()


count = 0

def train(my_data, bins, reg):

    global count
    count+=1

    # trainer = TPGMMTrainer.TPGMMTrainer(demo=[my_data[0], my_data[1],my_data[2],my_data[3],my_data[4],my_data[5]],
    #                                     file_name="file_name",
    #                                     n_rf=6*[bins],
    #                                     dt=0.01,
    #                                     reg=6*[reg],
    #                                     poly_degree=[25,25,25,25,25,25])

    #my_model = trainer.train(save=False)
    print (6*[bins])
    return  bins+reg #my_model['BIC']


if __name__ == '__main__':
    # #temp_test()
    my_data = read_data() 
    name = "opt_temp"

    model = pulp.LpProblem(name="small-problem", sense=pulp.LpMinimize)
    bins = pulp.LpVariable(name="bins", lowBound=1, upBound=100, cat='Integer')
    reg = pulp.LpVariable(name="reg", lowBound=0.0001, upBound=1.0, cat='Continues')

    model += train(my_data, bins, reg)
    status = model.solve()