import MySQLdb as mdb
import csv
import random
from sklearn.cross_validation import train_test_split
from Fingerprint import Fingerprint


class Data():
    def __init__(self, attributes, computeSamples=False, seed=42):
        self.seed = seed
        random.seed(seed)
        self.con = mdb.connect('localhost', 'root', 'bdd', 'fpdata')
        self.cur = self.con.cursor(mdb.cursors.DictCursor)
        self.train = list()
        self.test = list()
        self.computeSamples = computeSamples
        self.attributes = attributes

    def splitData(self, min_number_fp = 2, min_counter = 1000, max_counter = 100000):
        """
        Split the data in a train and test set

        :param min_number_fp: min value of the counter
        :param min_counter: min number of fingerprints for a given id
        :return: (train, test), respectively list of counters value for training and test set
        """
        if self.computeSamples:
            # We retrieve the id of the users having at least 2 fingerprints
            self.cur.execute(
                'SELECT id , count(*) AS nbFps FROM fpData where id != "" and id != "Not supported" AND counter < '+str(max_counter)+' AND counter > '+str(min_counter)+' GROUP BY id HAVING count(id) >= '+str(min_number_fp))
            multId = self.cur.fetchall()
            total = list()

            idString = "("
            for ids in multId:
                idString += "\"" + ids["id"] + "\","
            idString = idString[0: len(idString) - 1]
            idString += ")"

            self.cur.execute('SELECT counter from fpData WHERE id in ' + idString)
            counters = self.cur.fetchall()
            for counter in counters:
                total.append(counter["counter"])

            # we keep 5% of these counters for the test, the others go in the train
            train, test = train_test_split(total, train_size=0.95)
            # we get users with only 1 fingerprint
            self.cur.execute(
                'SELECT counter, id , count(*) AS nbFps FROM fpData where id != "" and id != "Not supported" AND counter < '+str(max_counter)+' AND counter > '+str(min_counter)+' GROUP BY id, counter HAVING count(id) = 1')
            singleFps = set()
            singId = self.cur.fetchall()
            cpt = 0
            for ids in singId:
                if cpt % 100 == 0:
                    print(cpt)
                cpt += 1
                singleFps.add(ids["counter"])

            singleFpsSelected = random.sample(singleFps, 250)
            test = test + singleFpsSelected

            # we save the result in 2 files so that we don't always have to compute the samples
            f = open("./samples/train.csv", 'w')
            for counter in train:
                f.write(str(counter) + "\n")

            f = open("./samples/test.csv", 'w')
            for counter in test:
                f.write(str(counter) + "\n")
        else:
            train = list()
            test = list()
            with open("./samples/train.csv", 'r') as trainFile:
                trainReader = csv.reader(trainFile, delimiter=',')
                for counter in trainReader:
                    train.append(int(counter[0]))

            with open("./samples/test.csv", 'r') as testFile:
                testReader = csv.reader(testFile, delimiter=',')
                for counter in testReader:
                    test.append(int(counter[0]))

        self.train = train
        self.test = test

        return train, test

    def getTrainSample(self):
        """
        :param attributes: List of attributes we want to obtain. Use constants defined in the class Fingerprint
        :return: trainSet, a list of Fingerprint objects
        """
        attributes = set(self.attributes).intersection(Fingerprint.MYSQL_ATTRIBUTES)
        attributes = ",".join(attributes)

        if len(self.train) == 0:
            self.splitData()

        counterString = "("
        for counter in self.train:
            counterString += str(counter) + ","

        counterString = counterString[0: len(counterString) - 1]
        counterString += ")"
        self.cur.execute(
            'SELECT '+attributes+' FROM fpData WHERE counter in ' + counterString)
        res = self.cur.fetchall()

        trainSet = list()
        for v in res:
            trainSet.append(Fingerprint(self.attributes, v))

        return trainSet

    def getTestSample(self):
        """
            :param attributes: List of attributes we want to obtain. Use constants defined in the class Fingerprint
            :return: trainSet, a list of Fingerprint objects
        """

        attributes = set(self.attributes).intersection(Fingerprint.MYSQL_ATTRIBUTES)
        attributes = ",".join(attributes)

        if len(self.test) == 0:
            self.splitData()

        counterString = "("
        for counter in self.test:
            counterString += str(counter) + ","


        counterString = counterString[0: len(counterString) - 1]
        counterString += ")"

        self.cur.execute(
            'SELECT '+attributes+' FROM fpData WHERE counter in ' + counterString)
        res = self.cur.fetchall()

        testSet = list()
        for v in res:
            testSet.append(Fingerprint(self.attributes, v))

        return testSet

    def getDataTest(self):
        attributes = set(self.attributes).intersection(Fingerprint.MYSQL_ATTRIBUTES)
        attributes = ",".join(attributes)

        if len(self.train) == 0:
            self.splitData()

        counterString = "("
        for counter in self.train:
            counterString += str(counter) + ","

        counterString = counterString[0: len(counterString) - 1]
        counterString += ")"

        self.cur.execute('SELECT '+attributes+' FROM fpData WHERE counter in (8242,8239)')
        res = self.cur.fetchall()
        fps = list()
        for v in res:
            fps.append(Fingerprint(self.attributes, v))

        return fps


