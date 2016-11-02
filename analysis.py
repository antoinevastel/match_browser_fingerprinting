import random
import MySQLdb as mdb
import sys
import re

from scipy.special._precompute.gammainc_asy import compute_a

"""
Standalone script to analyse data contained in amiunique database
"""

def getUsersWithNbFps(cur, nb_fp = 2):
    #we get the ids of all the users having at least n fingerprints
    cur.execute('SELECT id , count(*) AS nbFps FROM fpData where id != "" and id != "Not supported" GROUP BY id HAVING count(id) >='+str(nb_fp))
    return cur.fetchall()

def computeProbabilityChange(cur):
    probabilityChange = dict()
    probabilityChange["addressHttp"] = 0.0
    probabilityChange["userAgentHttp"] = 0.0
    probabilityChange["acceptHttp"] = 0.0
    probabilityChange["hostHttp"] = 0.0
    probabilityChange["connectionHttp"] = 0.0
    probabilityChange["encodingHttp"] = 0.0
    probabilityChange["languageHttp"] = 0.0
    probabilityChange["orderHttp"] = 0.0
    probabilityChange["pluginsJS"] = 0.0
    probabilityChange["platformJS"] = 0.0
    probabilityChange["cookiesJS"] = 0.0
    probabilityChange["dntJS"] = 0.0
    probabilityChange["timezoneJS"] = 0.0
    probabilityChange["resolutionJS"] = 0.0
    probabilityChange["localJS"] = 0.0
    probabilityChange["sessionJS"] = 0.0
    probabilityChange["IEDataJS"] = 0.0
    probabilityChange["fontsFlash"] = 0.0
    probabilityChange["resolutionFlash"] = 0.0
    probabilityChange["languageFlash"] = 0.0
    probabilityChange["platformFlash"] = 0.0
    probabilityChange["adBlock"] = 0.0
    probabilityChange["canvasJSHashed"] = 0.0

    nbFingerprints = 0.0
    cur.execute(
        'select * from fpData where id in (select id FROM fpData where time <= "2016-09-29 09:00:00" and time > "2016-02-16 09:00:00" and id != "" AND id != "Not supported" group by id HAVING count(id) > 1) order by id, time asc'
    )

    fps = cur.fetchall()
    prevId = None

    alreadySeen = dict()
    cpt = 0
    for fp in fps:
        print(cpt)
        cpt += 1
        print(prevId, fp["id"])
        if prevId != fp["id"]:
            #part just to assert that results are correctly order, which was not the case before !
            try:
                alr_s = alreadySeen[fp["id"]]
                if alr_s:
                    raise ValueError("Error : values are not ordered")
            except:
                pass
            previousFp = fp
            prevId = fp["id"]
            alreadySeen[fp["id"]] = True
        else:
            currentFp = fp
            # we compare the current fingerprint with the previous one (chronologically speaking) and we add 1
            # to probabablityChange[att] if there is a difference between previousFp[att] and currentFp[att]
            for attribute in probabilityChange:
                if currentFp[attribute] != previousFp[attribute]:
                    probabilityChange[attribute] += 1
            nbFingerprints += 1
            previousFp = currentFp
            prevId = fp["id"]


    for attribute in probabilityChange:
        probabilityChange[attribute] /= nbFingerprints
        print(attribute, probabilityChange[attribute])


def computeProbabilityNbPluginsChanges(cur):
    nbFingerprints = 0.0
    pIncrease = 0.0
    pDecrease = 0.0
    pSame = 0.0
    pActDeact = 0.0

    nbFingerprints = 0.0
    cur.execute(
        'select * from fpData where id in (select id FROM fpData where time <= "2016-09-29 09:00:00" and time > "2016-02-16 09:00:00" and id != "" AND id != "Not supported" group by id HAVING count(id) > 1) order by id, time asc'
    )

    fps = cur.fetchall()
    prevId = None

    alreadySeen = dict()
    cpt = 0
    for fp in fps:
        print(cpt)
        cpt += 1
        print(prevId, fp["id"])
        if prevId != fp["id"]:
            # part just to assert that results are correctly order, which was not the case before !
            try:
                alr_s = alreadySeen[fp["id"]]
                if alr_s:
                    raise ValueError("Error : values are not ordered")
            except:
                pass
            previousFp = fp
            prevId = fp["id"]
            alreadySeen[fp["id"]] = True
        else:
            currentFp = fp
            if (currentFp["platformJS"] == "no JS" and previousFp["platformJS"] != "no JS") or \
                    (currentFp["platformJS"] != "no JS" and previousFp["platformJS"] == "no JS"):
                pActDeact += 1.0
            else:
                # we compare the number of plugins of the current fingerprint with the previous one (chronologically speaking)
                nbPluginsCurrent = len(re.findall("Plugin [0-9]+: ([a-zA-Z -.]+)", currentFp["pluginsJS"]))
                nbPluginsPrevious = len(re.findall("Plugin [0-9]+: ([a-zA-Z -.]+)", previousFp["pluginsJS"]))

                print(nbPluginsCurrent, nbPluginsPrevious)

                if nbPluginsCurrent > nbPluginsPrevious:
                    pIncrease += 1.0
                elif nbPluginsCurrent < nbPluginsPrevious:
                    pDecrease += 1.0
                else:
                    pSame += 1.0

            nbFingerprints += 1
            previousFp = currentFp
            prevId = fp["id"]

    pIncrease = pIncrease / nbFingerprints
    pDecrease = pDecrease / nbFingerprints
    pSame = pSame / nbFingerprints
    pActDeact = pActDeact / nbFingerprints

    print(pIncrease, pDecrease, pSame, pActDeact)

def computeProbabilityTurnOffFlash(cur):
    nbFingerprints = 0.0
    pChangeLanguage = 0.0
    pChangeResolution = 0.0
    pChangePlatform = 0.0

    nd = "Flash not detected"
    d = "Flash detected but not activated (click-to-play)"

    nbFingerprints = 0.0
    cur.execute(
        'select * from fpData where id in (select id FROM fpData where time <= "2016-09-29 09:00:00" and time > "2016-02-16 09:00:00" and id != "" AND id != "Not supported" group by id HAVING count(id) > 1) order by id, time asc'
    )

    fps = cur.fetchall()
    prevId = None

    alreadySeen = dict()
    cpt = 0
    for fp in fps:
        print(cpt)
        cpt += 1
        print(prevId, fp["id"])
        if prevId != fp["id"]:
            # part just to assert that results are correctly order, which was not the case before !
            try:
                alr_s = alreadySeen[fp["id"]]
                if alr_s:
                    raise ValueError("Error : values are not ordered")
            except:
                pass
            previousFp = fp
            prevId = fp["id"]
            alreadySeen[fp["id"]] = True
        else:
            currentFp = fp
            if ((currentFp["platformFlash"] == nd or currentFp["platformFlash"] == d) and \
                        (previousFp["platformFlash"] != nd and previousFp["platformFlash"] != d)) or \
                    ((currentFp["platformFlash"] != nd and currentFp["platformFlash"] != d) and \
                             (previousFp["platformFlash"] == nd or previousFp["platformFlash"] == d)):
                pChangePlatform += 1.0

            if ((currentFp["resolutionFlash"] == nd or currentFp["resolutionFlash"] == d) and \
                        (previousFp["resolutionFlash"] != nd and previousFp["resolutionFlash"] != d)) or \
                    ((currentFp["resolutionFlash"] != nd and currentFp["resolutionFlash"] != d) and \
                             (previousFp["resolutionFlash"] == nd or previousFp["resolutionFlash"] == d)):
                pChangeResolution += 1.0

            if ((currentFp["languageFlash"] == nd or currentFp["languageFlash"] == d) and \
                        (previousFp["languageFlash"] != nd and previousFp["languageFlash"] != d)) or \
                    ((currentFp["languageFlash"] != nd and currentFp["languageFlash"] != d) and \
                             (previousFp["languageFlash"] == nd or previousFp["languageFlash"] == d)):
                pChangeLanguage += 1.0

            nbFingerprints += 1
            previousFp = currentFp
            prevId = fp["id"]


    pChangePlatform = pChangePlatform / nbFingerprints
    pChangeResolution = pChangeResolution / nbFingerprints
    pChangeLanguage = pChangeLanguage / nbFingerprints

    print(pChangePlatform, pChangeResolution, pChangeLanguage)
    #0.204459765162 0.204459765162 0.204459765162

def computeProbabilityTurnOffJs(cur):
    nbFingerprints = 0.0
    pChange = 0.0


    nbFingerprints = 0.0
    cur.execute(
        'select * from fpData where id in (select id FROM fpData where time <= "2016-09-29 09:00:00" and time > "2016-02-16 09:00:00" and id != "" AND id != "Not supported" group by id HAVING count(id) > 1) order by id, time asc'
    )

    fps = cur.fetchall()
    prevId = None

    alreadySeen = dict()
    cpt = 0

    for fp in fps:
        print(cpt)
        cpt += 1
        print(prevId, fp["id"])
        if prevId != fp["id"]:
            # part just to assert that results are correctly order, which was not the case before !
            try:
                alr_s = alreadySeen[fp["id"]]
                if alr_s:
                    raise ValueError("Error : values are not ordered")
            except:
                pass
            previousFp = fp
            prevId = fp["id"]
            alreadySeen[fp["id"]] = True
        else:
            currentFp = fp

            if (currentFp["platformJS"] == "no JS" and previousFp["platformJS"] != "no JS") or \
                    (currentFp["platformJS"] != "no JS" and previousFp["platformJS"] == "no JS"):
                pChange += 1.0

            nbFingerprints += 1
            previousFp = currentFp
            prevId = fp["id"]

    pChange = pChange / nbFingerprints
    print(pChange)

def computeChangesFonts(cur):
    nbFingerprints = 0.0
    pIncrease = 0.0
    pDecrease = 0.0
    pSame = 0.0
    pActDeact = 0.0
    nd = "Flash not detected"
    d = "Flash detected but not activated (click-to-play)"

    nbFingerprints = 0.0
    cur.execute(
        'select * from fpData where id in (select id FROM fpData where time <= "2016-09-29 09:00:00" and time > "2016-02-16 09:00:00" and id != "" AND id != "Not supported" group by id HAVING count(id) > 1) order by id, time asc'
    )

    fps = cur.fetchall()
    prevId = None

    alreadySeen = dict()
    cpt = 0

    for fp in fps:
        print(cpt)
        cpt += 1
        print(prevId, fp["id"])
        if prevId != fp["id"]:
            # part just to assert that results are correctly order, which was not the case before !
            try:
                alr_s = alreadySeen[fp["id"]]
                if alr_s:
                    raise ValueError("Error : values are not ordered")
            except:
                pass
            previousFp = fp
            prevId = fp["id"]
            alreadySeen[fp["id"]] = True
        else:
            currentFp = fp
            if ((currentFp["platformFlash"] == nd or currentFp["platformFlash"] == d) and \
                        (previousFp["platformFlash"] != nd and previousFp["platformFlash"] != d)) or \
                    ((currentFp["platformFlash"] != nd and currentFp["platformFlash"] != d) and \
                             (previousFp["platformFlash"] == nd or previousFp["platformFlash"] == d)):
                pActDeact += 1.0
            else:
                # we compare the number of fonts of the current fingerprint with the previous one (chronologically speaking)
                nbFontsCurrent = len(currentFp["fontsFlash"].split("_"))
                nbFontsPrevious = len(previousFp["fontsFlash"].split("_"))

                if nbFontsCurrent > nbFontsPrevious:
                    pIncrease += 1.0
                elif nbFontsCurrent < nbFontsPrevious:
                    pDecrease += 1.0
                else:
                    pSame += 1.0

            nbFingerprints += 1
            previousFp = currentFp
            prevId = fp["id"]


    pIncrease = pIncrease / nbFingerprints
    pDecrease = pDecrease / nbFingerprints
    pSame = pSame / nbFingerprints
    pActDeact = pActDeact / nbFingerprints


    print(pIncrease, pDecrease, pSame, pActDeact)
    #0.0406020301015 0.0507525376269 0.908645432272

def main():
    con = mdb.connect('localhost', 'root', 'bdd', 'fpdata')
    cur = con.cursor(mdb.cursors.DictCursor)
    # multId = getUsersWithNbFps(cur, 2)
    # computeProbabilityChange(cur)
    # computeProbabilityTurnOffFlash(cur)
    # computeProbabilityTurnOffJs(cur)
    # computeProbabilityNbPluginsChanges(cur)
    computeChangesFonts(cur)

    #We keep 66% of the id
    #multIdStats = list()
    #i = 0
    #for indiv in multId:
    #	if i%2 == 0 or i%3 ==0:
    #		multIdStats.append(indiv)

    #	i += 1

    #computeProbabilityChange(cur, multId)
    #computeProbabilityNbPluginsChanges(cur, multId)
    con.close()

if __name__ == "__main__":
    main()