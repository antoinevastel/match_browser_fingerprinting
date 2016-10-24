from Fingerprint import Fingerprint
from Data import Data
from Algorithm import Algorithm

def main():
    #TODO add "attributes" in Data class
    attributes = Fingerprint.INFO_ATTRIBUTES + Fingerprint.HTTP_ATTRIBUTES + Fingerprint.JAVASCRIPT_ATTRIBUTES
    d = Data(attributes, computeSamples = False)
    trainIndices, testIndices = d.splitData(min_number_fp = 2, min_counter = 1000, max_counter = 90000)
    algo = Algorithm(d.getTrainSample(), d.getTestSample(), attributes)
    # algo.computeRegressionInput()
    # algo.predictXGboost()

    activation_functions = ['identity', 'logistic', 'tanh', 'relu']
    solvers = ["lbfgs", "adam"]
    hidden_layers_sizes = [(3, 2), (4,2), (5,2), (6,2), (3,3), (4,3), (5,3), (6,3), (2,2,2), (3,3,2), (4,4,2)]

    algo.trainNNModel(hidden_layer_sizes = (3,3,2), activation="logistic")
    algo.predictNN()
    #  algo.predict()
    algo.writeSubmission()
    print(algo.evalPrecision())


if __name__ == "__main__":
    main()
