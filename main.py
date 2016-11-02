from Fingerprint import Fingerprint
from Data import Data
from Algorithm import Algorithm


def runGridSearch():
    attributes = Fingerprint.INFO_ATTRIBUTES + Fingerprint.HTTP_ATTRIBUTES + Fingerprint.JAVASCRIPT_ATTRIBUTES
    min_numbers_fp = [2, 3, 4, 5]
    max_counters = [80000, 100000, 130000, 170000, 200000, 220000]
    thresholds = [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 660]
    activation_functions = ['identity', 'logistic', 'tanh', 'relu']
    solvers = ["lbfgs", "adam"]
    hidden_layers_sizes = [(3, 2), (4, 2), (5, 2), (6, 2), (3, 3), (4, 3), (5, 3), (6, 3), (2, 2, 2), (3, 3, 2), (4, 4, 2)]
    algo_thresholds = [0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
    model_name = "NeuralNetwork"

    for min_number_fp in min_numbers_fp:
        for max_counter in max_counters:
            for i in range(0, len(thresholds)-1):
                d = Data(attributes, computeSamples = True)
                d.splitData(min_number_fp = min_number_fp, min_counter = 1000, max_counter = max_counter)
                algo = Algorithm(attributes)
                algo.setTrainSet(d.getTrainSample())
                algo.setTestSet(d.getTestSample())
                algo.computeRegressionInput(thresholds[i], thresholds[i+1])

                for activation_function in activation_functions:
                    for solver in solvers:
                        for hidden_layer_size in hidden_layers_sizes:
                            algo.trainNNModel(hidden_layer_sizes=hidden_layer_size, activation=activation_function, solver=solver)
                            for algo_threshold in algo_thresholds:
                                algo.predictNN(threshold = algo_threshold)
                                algo.writeSubmission()
                                s_parameters = ("%d;%d;%d;%d;%s;%s;%s;%f" % (min_number_fp, max_counter, thresholds[i],\
                                                thresholds[i+1], activation_function, solver, str(hidden_layer_size), algo_threshold))
                                print(s_parameters)
                                print(algo.evalPrecision(model_name, s_parameters))

def runSinglePrediction(attributes, min_number_fp, min_counter, max_counter, threshold_min, threshold_max, activation_function, solver,\
                        hidden_layers_size, algo_threshold, model_name):
    d = Data(attributes, computeSamples=True)
    d.splitData(min_number_fp=min_number_fp, min_counter=min_counter, max_counter=max_counter)
    algo = Algorithm(attributes)
    algo.setTrainSet(d.getTrainSample())
    algo.setTestSet(d.getTestSample())
    algo.computeRegressionInput(threshold_min, threshold_max)
    algo.trainNNModel(hidden_layer_sizes=hidden_layers_size, activation=activation_function, solver=solver)
    algo.predictNN(threshold=algo_threshold)
    algo.writeSubmission()
    s_parameters = ("%d;%d;%d;%d;%d;%s;%s;%s;%f" % (min_number_fp, min_counter, max_counter, threshold_min, \
                                                 threshold_max, activation_function, solver, str(hidden_layers_size),
                                                 algo_threshold))
    print(s_parameters)
    print(algo.evalPrecision(model_name, s_parameters))


def main():
    attributes = Fingerprint.INFO_ATTRIBUTES + Fingerprint.HTTP_ATTRIBUTES + Fingerprint.JAVASCRIPT_ATTRIBUTES
    runSinglePrediction(attributes, min_number_fp = 2, min_counter = 78000,max_counter = 220000, threshold_min = 100, threshold_max = 200,\
                        activation_function = "relu", solver = "adam",\
                        hidden_layers_size = (4,2), algo_threshold = 0.93, model_name = "NeuralNetwork")

if __name__ == "__main__":
    main()
