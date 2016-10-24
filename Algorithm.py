from sklearn.linear_model import LogisticRegression

from Fingerprint import Fingerprint
import csv
import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

import pickle


class Algorithm():
    def __init__(self, trainSet, testSet, attributes):
        self.trainSet = trainSet
        self.testSet = testSet
        self.dicResTrain = dict()
        self.predictions = dict()
        self.attributes = attributes
        self.model = None
        self.isTrained = False


    def generateHeader(self):
        header = []

        for attribute in self.attributes:
            if attribute == Fingerprint.ID:
                header.insert(0, Fingerprint.ID)
            elif attribute == Fingerprint.BROWSER_FAMILY:
               header.append(Fingerprint.BROWSER_FAMILY)
            elif attribute == Fingerprint.OS:
                header.append(Fingerprint.OS)
            elif attribute == Fingerprint.MAJOR_BROWSER_VERSION:
                header.append(Fingerprint.MAJOR_BROWSER_VERSION)
            elif attribute == Fingerprint.LANGUAGE_HTTP:
                header.append(Fingerprint.LANGUAGE_HTTP)
            elif attribute == Fingerprint.ACCEPT_HTTP:
                header.append(Fingerprint.ACCEPT_HTTP)
            elif attribute == Fingerprint.ENCODING_HTTP:
                header.append(Fingerprint.ENCODING_HTTP)
            elif attribute == Fingerprint.ADDRESS_HTTP:
                header.append(Fingerprint.ADDRESS_HTTP)
            elif attribute == Fingerprint.TIMEZONE_JS:
                header.append(Fingerprint.TIMEZONE_JS)
            elif attribute == Fingerprint.PLUGINS_JS:
                header.append("PluginsSubset")
                header.append("SamePlugins")
            elif attribute == Fingerprint.RESOLUTION_JS:
                header.append(Fingerprint.RESOLUTION_JS)
            elif attribute == Fingerprint.AD_BLOCK:
                header.append(Fingerprint.AD_BLOCK)
            elif attribute == Fingerprint.CANVAS_JS_HASHED:
                header.append(Fingerprint.CANVAS_JS_HASHED)
            elif attribute == Fingerprint.PLATFORM_JS:
                header.append(Fingerprint.PLATFORM_JS)
            elif attribute == Fingerprint.DNT_JS:
                header.append(Fingerprint.DNT_JS)
            elif attribute == Fingerprint.COOKIES_JS:
                header.append(Fingerprint.COOKIES_JS)
            elif attribute == Fingerprint.LOCAL_JS:
                header.append(Fingerprint.LOCAL_JS)
            elif attribute == Fingerprint.PLATFORM_FLASH:
                header.append(Fingerprint.PLATFORM_FLASH)
            elif attribute == Fingerprint.FONTS_FLASH:
                header.append("SameFonts")
                header.append("FontsSubset")
            elif attribute == Fingerprint.LANGUAGE_FLASH:
                header.append(Fingerprint.LANGUAGE_FLASH)
            elif attribute == Fingerprint.RESOLUTION_FLASH:
                header.append(Fingerprint.RESOLUTION_FLASH)

        return ",".join(header)+"\n"

    def computeSimilarityVector(self, fpFixed, fpCompared):
        similarity_vector = []
        jsActivated = not (fpFixed.hasJsActivated()) or not (fpCompared.hasJsActivated())
        # jsActivated = fpFixed.hasJsActivated() and fpCompared.hasJsActivated()
        flashActivated = not (fpFixed.hasFlashActivated()) or not (fpCompared.hasFlashActivated())
        # flashActivated = fpFixed.hasFlashActivated() and fpCompared.hasFlashActivated()
        for attribute in self.attributes:
            if attribute == Fingerprint.ID:
                valToInsert = ("0" if fpFixed.belongToSameUser(fpCompared) else "1")
                similarity_vector.insert(0, valToInsert)
            elif attribute == Fingerprint.BROWSER_FAMILY:
                similarity_vector.append("0") if fpFixed.hasSameBrowser(fpCompared) else similarity_vector.append(
                    "1")
            elif attribute == Fingerprint.OS:
                similarity_vector.append("0") if fpFixed.hasSameOs(fpCompared) else similarity_vector.append(
                    "1")
            elif attribute == Fingerprint.MAJOR_BROWSER_VERSION:
                similarity_vector.append("0") if fpFixed.hasHighestBrowserVersion(fpCompared) else similarity_vector.append(
                    "1")
            elif attribute == Fingerprint.LANGUAGE_HTTP:
                similarity_vector.append("0") if fpFixed.hasSameHttpLanguages(fpCompared) else similarity_vector.append(
                    "1")
            elif attribute == Fingerprint.ACCEPT_HTTP:
                similarity_vector.append("0") if fpFixed.hasSameAcceptHttp(fpCompared) else similarity_vector.append("1")
            elif attribute == Fingerprint.ENCODING_HTTP:
                similarity_vector.append("0") if fpFixed.hasSameEncodingHttp(fpCompared) else similarity_vector.append(
                    "1")
            elif attribute == Fingerprint.ADDRESS_HTTP:
                similarity_vector.append("0") if fpFixed.hasSameAddressHttp(fpCompared) else similarity_vector.append(
                    "1")
            elif attribute == Fingerprint.TIMEZONE_JS:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSameTimezone(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.PLUGINS_JS:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.arePluginsSubset(fpCompared) else similarity_vector.append(
                    "1")
                    similarity_vector.append("0") if fpFixed.hasSamePlugins(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
                    similarity_vector.append("2")
            elif attribute == Fingerprint.RESOLUTION_JS:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSameResolution(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.AD_BLOCK:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSameAdblock(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.CANVAS_JS_HASHED:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSameCanvasJsHashed(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.PLATFORM_JS:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSamePlatformJs(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.DNT_JS:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSameDnt(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.COOKIES_JS:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSameCookie(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.LOCAL_JS:
                if not jsActivated:
                    similarity_vector.append("0") if fpFixed.hasSameLocalJs(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.PLATFORM_FLASH:
                if not flashActivated:
                    similarity_vector.append("0") if fpFixed.hasSamePlatformFlash(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.FONTS_FLASH:
                if not flashActivated:
                    similarity_vector.append("0") if fpFixed.hasSameFonts(fpCompared) else similarity_vector.append(
                    "1")
                    similarity_vector.append("0") if fpFixed.areFontsSubset(fpCompared) else similarity_vector.append(
                        "1")
                else:
                    similarity_vector.append("2")
                    similarity_vector.append("2")
            elif attribute == Fingerprint.LANGUAGE_FLASH:
                if not flashActivated:
                    similarity_vector.append("0") if fpFixed.hasSameLanguageFlash(fpCompared) else similarity_vector.append("1")
                else:
                    similarity_vector.append("2")
            elif attribute == Fingerprint.RESOLUTION_FLASH:
                if not flashActivated:
                    similarity_vector.append("0") if fpFixed.hasSameResolutionFlash(fpCompared) else similarity_vector.append(
                    "1")
                else:
                    similarity_vector.append("2")

        return ",".join(similarity_vector)


    def computeRegressionInput(self):
        print("Start computeRegressionInput")
        # result is the string describing the results from all the points we are going to test
        # to compare two fingerprints

        # We compare every fingerprints with all the other except itself
        f = open("./samples/regInput.csv", 'w')
        # f.write(
        #     "sameUser,browser,os,browserVersion,httpLanguages,acceptHttp,encodingHttp,timezoneJs,pluginsSubset,resolutionJs,adblock,plugins,canvasJs,platformJs,dntJs,cookiesJs,localJs,flashBlockedExt,fontsSubset,fonts,platformFlash,resolutionFlash\n")

        f.write(self.generateHeader())

        for i in range(len(self.trainSet)):
            if i % 500 == 0:
                print(i)
            fpFixed = self.trainSet[i]
            for j in range(i + 1, len(self.trainSet)):
                fpCompared = self.trainSet[j]
                if fpFixed.getId() == fpCompared.getId():
                    result = self.computeSimilarityVector(fpFixed, fpCompared)
                    # result = self.computeSimilarity(fpFixed, fpCompared)
                    f.write(result + "\n")

        for i in range(len(self.trainSet)):
            if i % 500 == 0:
                print(i)
            # compareWith = random.randint(250, 350)
            compareWith = random.randint(200, 300)
            fpFixed = self.trainSet[i]
            for j in range(i + 1, len(self.trainSet)):
                fpCompared = self.trainSet[j]
                if j % compareWith == 0 and fpFixed.getId() != fpCompared.getId():
                    result = self.computeSimilarityVector(fpFixed, fpCompared)
                    # result = self.computeSimilarity(fpFixed, fpCompared)
                    f.write(result + "\n")

        f.close()

    def predict(self):
        print("Start Predict")
        df = pd.read_csv("./samples/regInput.csv")
        cols = df.columns.tolist()

        y = df[cols[0]]  # variable to predict
        X = df[cols[1:]]
        y = np.ravel(y)
        model = LogisticRegression(n_jobs = 3)
        # model = RandomForestClassifier(n_estimators=5, n_jobs=3)
        model = model.fit(X, y)

        cpt = 0
        for fpTest in self.testSet:
            print(cpt)
            cpt += 1
            f = open("./samples/regInputPred.csv", 'w')
            f.write(self.generateHeader())
            for fpTrain in self.trainSet:
                resultComparaison = self.computeSimilarityVector(fpTest, fpTrain)
                f.write(resultComparaison + "\n")

            f.close()
            dfPredict = pd.read_csv("./samples/regInputPred.csv")
            cols = dfPredict.columns.tolist()
            Xp = dfPredict[cols[1:]]
            predicted = model.predict_proba(Xp)
            nearest = (-predicted[:, 0]).argsort()[:30]

            if predicted[nearest[0], 0] > 0.93:
                self.predictions[fpTest.counter] = self.trainSet[nearest[0]].id
            else:
                self.predictions[fpTest.counter] = None

            res = fpTest.id == self.trainSet[nearest[0]].id
            print(
                "Prediction : " + str(fpTest.counter) + " ," + str(self.predictions[fpTest.counter]) + ", " + str(res))

    def predictXGboost(self):
        print("Start Predict")
        df = pd.read_csv("./samples/regInput.csv")
        cols = df.columns.tolist()

        y = df[cols[0]]  # variable to predict
        le = LabelEncoder()
        y = le.fit_transform(y)

        X = df[cols[1:]]

        train_X = X.as_matrix()
        # train_y = y.as_matrix()
        gbm = xgb.XGBClassifier(max_depth=5, n_estimators=250, learning_rate=0.05).fit(train_X, y)

        cpt = 0
        for fpTest in self.testSet:
            print(cpt)
            cpt += 1
            f = open("./samples/regInputPred.csv", 'w')
            f.write(
                "sameUser,browser,os,browserVersion,httpLanguages,acceptHttp,encodingHttp,timezoneJs,pluginsSubset,resolutionJs,adblock,plugins,canvasJs,platformJs,dntJs,cookiesJs,localJs,flashBlockedExt,fontsSubset,fonts,platformFlash,resolutionFlash\n")
            for fpTrain in self.trainSet:
                resultComparaison = self.computeSimilirarity(fpTest, fpTrain)
                f.write(resultComparaison + "\n")

            f.close()
            dfPredict = pd.read_csv("./samples/regInputPred.csv")
            cols = dfPredict.columns.tolist()
            yp = dfPredict[cols[0]]
            Xp = dfPredict[cols[1:]]
            predicted = gbm.predict_proba(Xp.as_matrix())

            nearest = (-predicted[:, 0]).argsort()[:30]

            if predicted[nearest[0], 0] > 0.93:
                self.predictions[fpTest.counter] = self.trainSet[nearest[0]].id
            else:
                self.predictions[fpTest.counter] = None

            res = fpTest.id == self.trainSet[nearest[0]].id
            print(
                "Prediction : " + str(fpTest.counter) + " ," + str(self.predictions[fpTest.counter]) + ", " + str(res))

    #TODO use warm restart
    def trainNNModel(self, hidden_layer_sizes, activation, solver):
        print("Start training neural network")
        df = pd.read_csv("./samples/regInput.csv")
        cols = df.columns.tolist()

        y = df[cols[0]]  # variable to predict
        le = LabelEncoder()
        y = le.fit_transform(y)
        X = df[cols[1:]]
        # TODO maybe we can delete as_matrix
        train_X = X.as_matrix()
        y = np.ravel(y)
        #4,2 -> 78.7
        #5,2 -> 78.8
        #15,2 -> 75.7
        self.model = MLPClassifier(activation=activation, solver=solver, alpha=1e-3, hidden_layer_sizes=hidden_layer_sizes, random_state=1)
        self.model.fit(train_X, y)
        self.isTrained = True

    def predictNN(self):
        if not self.isTrained:
            raise ValueError("Model is not trained")

        print("Start Predict")
        cpt = 0
        for fpTest in self.testSet:
            print(cpt)
            cpt += 1
            f = open("./samples/regInputPred.csv", 'w')
            f.write(self.generateHeader())
            for fpTrain in self.trainSet:
                resultComparaison = self.computeSimilarityVector(fpTest, fpTrain)
                f.write(resultComparaison + "\n")

            f.close()
            dfPredict = pd.read_csv("./samples/regInputPred.csv")
            cols = dfPredict.columns.tolist()
            Xp = dfPredict[cols[1:]]

            predicted = self.model.predict_proba(Xp.as_matrix())

            nearest = (-predicted[:, 0]).argsort()[:30]
            if predicted[nearest[0], 0] > 0.90:
                self.predictions[fpTest.getCounter()] = self.trainSet[nearest[0]].getId()
            else:
                self.predictions[fpTest.getCounter()] = None

            res = fpTest.getId() == self.trainSet[nearest[0]].getId()
            print("Prediction : " + str(fpTest.getCounter()) + " ," + str(self.predictions[fpTest.getCounter()]) + ", " + str(res))

    def writeSubmission(self):
        if len(self.predictions) == 0:
            self.predict()

        f = open("./samples/submission.csv", 'w')
        for counter in self.predictions:
            f.write(str(counter) + "," + str(self.predictions[counter]) + "\n")

    def evalPrecision(self):
        idsTrain = set()
        for fp in self.trainSet:
            idsTrain.add(fp.getId())

        with open('./samples/submission.csv', 'r') as submissionFile:
            submissionReader = csv.reader(submissionFile, delimiter=',')
            for row in submissionReader:
                self.predictions[int(row[0])] = row[1]

        precision = 0.0
        noneError = 0.0
        badIdError = 0.0
        for fpTest in self.testSet:
            if self.predictions[fpTest.getCounter()] == fpTest.getId():
                precision += 1.0
            elif self.predictions[fpTest.getCounter()] == "None" and fpTest.getId() not in idsTrain:
                precision += 1.0
            elif self.predictions[fpTest.getCounter()] == "None" and fpTest.getId() in idsTrain:
                noneError += 1.0
            elif self.predictions[fpTest.getCounter()] != fpTest.getId():
                badIdError += 1.0

        print("noneError : " + str(noneError / float(len(self.testSet))))
        print("badIdError : " + str(badIdError / float(len(self.testSet))))
        return precision / float(len(self.testSet))







