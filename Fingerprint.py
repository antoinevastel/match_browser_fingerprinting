from ua_parser import user_agent_parser
import re

class Fingerprint():

    ID = "id"
    COUNTER = "counter"

    #HTTP attributes
    ACCEPT_HTTP = "acceptHttp"
    LANGUAGE_HTTP = "languageHttp"
    USER_AGENT_HTTP = "userAgentHttp"
    ORDER_HTTP = "orderHttp"
    ADDRESS_HTTP = "addressHttp"
    CONNECTION_HTTP = "connectionHttp"
    ENCODING_HTTP = "encodingHttp"
    HOST_HTTP = "hostHttp"

    BROWSER_FAMILY = "browserFamily"
    MINOR_BROWSER_VERSION = "minorBrowserVersion"
    MAJOR_BROWSER_VERSION = "majorBrowserVersion"
    OS = "os"

    #Javascript attributes
    COOKIES_JS = "cookiesJS"
    RESOLUTION_JS = "resolutionJS"
    TIMEZONE_JS = "timezoneJS"
    PLUGINS_JS = "pluginsJS"
    SESSION_JS = "sessionJS"
    DNT_JS = "dntJS"
    IE_DATA_JS = "IEDataJS"
    CANVAS_JS_HASHED = "canvasJSHashed"
    LOCAL_JS = "localJS"
    PLATFORM_JS = "platformJS"
    AD_BLOCK = "adBlock"

    NB_PLUGINS = "nbPlugins"
    PLATFORM_INCONSISTENCY = "platformInconsistency"

    #Flash attributes
    PLATFORM_FLASH = "platformFlash"
    FONTS_FLASH = "fontsFlash"
    LANGUAGE_FLASH = "languageFlash"
    RESOLUTION_FLASH = "resolutionFlash"

    NB_FONTS = "nbFonts"
    LANGUAGE_INCONSISTENCY = "languageInconsistency"



    INFO_ATTRIBUTES = [ID, COUNTER]

    HTTP_ATTRIBUTES = [ACCEPT_HTTP, LANGUAGE_HTTP, USER_AGENT_HTTP, ORDER_HTTP, ADDRESS_HTTP, CONNECTION_HTTP,\
                       ENCODING_HTTP, HOST_HTTP, BROWSER_FAMILY, MINOR_BROWSER_VERSION, MAJOR_BROWSER_VERSION, OS]

    JAVASCRIPT_ATTRIBUTES = [COOKIES_JS, RESOLUTION_JS, TIMEZONE_JS, PLUGINS_JS, SESSION_JS, DNT_JS, IE_DATA_JS, CANVAS_JS_HASHED, \
                             LOCAL_JS, PLATFORM_JS, AD_BLOCK, NB_PLUGINS, PLATFORM_INCONSISTENCY]

    FLASH_ATTRIBUTES = [PLATFORM_FLASH, FONTS_FLASH, LANGUAGE_FLASH, RESOLUTION_FLASH, NB_FONTS, LANGUAGE_INCONSISTENCY]

    MYSQL_ATTRIBUTES = set([COUNTER, ID, ADDRESS_HTTP, USER_AGENT_HTTP, ACCEPT_HTTP, HOST_HTTP, CONNECTION_HTTP, ENCODING_HTTP, \
                        LANGUAGE_HTTP, ORDER_HTTP, PLUGINS_JS, PLATFORM_JS, COOKIES_JS, DNT_JS, TIMEZONE_JS, \
                        RESOLUTION_JS, LOCAL_JS, SESSION_JS, IE_DATA_JS, CANVAS_JS_HASHED, FONTS_FLASH, RESOLUTION_FLASH, LANGUAGE_FLASH, \
                        PLATFORM_FLASH, AD_BLOCK])


    def __init__(self, list_attributes, val_attributes):
        self.val_attributes = dict()
        for attribute in list_attributes:
            try:
                self.val_attributes[attribute] = val_attributes[attribute]
            except:
                #exception happens when the value of the attribute has to be determined dynamically (ie nb plugins, browser version)
                self.val_attributes[attribute] = None


        if Fingerprint.PLUGINS_JS in list_attributes:
            self.val_attributes[Fingerprint.NB_PLUGINS] = self.getNumberOfPlugins()


        if Fingerprint.USER_AGENT_HTTP in list_attributes:
            parsedUa = user_agent_parser.Parse(val_attributes[Fingerprint.USER_AGENT_HTTP])
            self.val_attributes[Fingerprint.BROWSER_FAMILY] = parsedUa["user_agent"]["family"]
            self.val_attributes[Fingerprint.MINOR_BROWSER_VERSION] = parsedUa["user_agent"]["minor"]
            self.val_attributes[Fingerprint.MAJOR_BROWSER_VERSION] = parsedUa["user_agent"]["major"]
            self.val_attributes[Fingerprint.OS] = parsedUa["os"]["family"]

        if Fingerprint.NB_FONTS in list_attributes:
            self.val_attributes[Fingerprint.NB_FONTS] = self.getNumberFonts()

        if Fingerprint.LANGUAGE_INCONSISTENCY in list_attributes and self.hasFlashActivated():
            self.val_attributes[Fingerprint.LANGUAGE_INCONSISTENCY] = self.hasLanguageInconsistency()

        if Fingerprint.LANGUAGE_INCONSISTENCY in list_attributes and self.hasJsActivated():
            self.val_attributes[Fingerprint.LANGUAGE_INCONSISTENCY] = self.hasPlatformInconsistency()


    def __str__(self):
        s = ""
        for k, v in self.val_attributes.items():
            s += ("%s : %s \n" % (k,v))
        return s

    def hasJsActivated(self):
        try:
            return self.val_attributes[Fingerprint.PLATFORM_JS] != "no JS"
        except:
            return False


    def hasFlashActivated(self):
        try:
            return self.val_attributes[Fingerprint.FONTS_FLASH] != "Flash detected but not activated (click-to-play)" and \
               self.val_attributes[Fingerprint.FONTS_FLASH] != "Flash not detected" and \
               self.val_attributes[Fingerprint.FONTS_FLASH] != "Flash detected but blocked by an extension"
        except:
            return False


    def getFonts(self):
        if self.hasFlashActivated():
            return self.val_attributes[Fingerprint.FONTS_FLASH].split("_")
        else:
            return []

    def getNumberFonts(self):
        return len(self.getFonts())


    def getPlugins(self):
        if self.hasJsActivated():
            return re.findall("Plugin [0-9]+: ([a-zA-Z -.]+)", self.val_attributes[Fingerprint.PLUGINS_JS])
        else:
            return []

    def getNumberOfPlugins(self):
        return self.val_attributes[Fingerprint.NB_PLUGINS]

    def getBrowser(self):
        return self.val_attributes[Fingerprint.BROWSER_FAMILY]

    def getOs(self):
        return self.val_attributes[Fingerprint.OS]

    def hasLanguageInconsistency(self):
        if self.hasFlashActivated():
            try:
                langHttp = self.val_attributes[Fingerprint.LANGUAGE_HTTP][0:2].lower()
                langFlash = self.val_attributes[Fingerprint.LANGUAGE_FLASH][0:2].lower()
                return not (langHttp == langFlash)
            except:
                return True
        else:
            raise ValueError("Flash is not activated")

    def hasPlatformInconsistency(self):
        if self.hasJsActivated():
            try:
                platUa = self.getOs()[0:3].lower()
                if self.hasFlashActivated():
                    platFlash = self.val_attributes[Fingerprint.PLATFORM_FLASH][0:3].lower()
                    return not (platUa == platFlash)
                else:
                    platJs = self.val_attributes[Fingerprint.PLATFORM_JS][0:3].lower()
                    return not (platUa == platJs)
            except:
                return True
        else:
            raise ValueError("Javascript is not activated")

    def hasFlashBlockedByExtension(self):
        return self.val_attributes[Fingerprint.PLATFORM_FLASH] == "Flash detected but blocked by an extension"

    ##########

    # Methods to compare 2 Fingerprints :

    ##########

    def hasSameOs(self, fp):
        return self.getOs() == fp.getOs()

    def hasSameBrowser(self, fp):
        return self.getBrowser() == fp.getBrowser()

    def hasSameTimezone(self, fp):
        return self.val_attributes[Fingerprint.TIMEZONE_JS] == fp.val_attributes[Fingerprint.TIMEZONE_JS]

    def hasSameResolution(self, fp):
        return self.val_attributes[Fingerprint.RESOLUTION_JS] == fp.val_attributes[Fingerprint.RESOLUTION_JS]

    def hasSameAdblock(self, fp):
        return self.val_attributes[Fingerprint.AD_BLOCK] == fp.val_attributes[Fingerprint.AD_BLOCK]

    def hasSameHttpLanguages(self, fp):
        return self.val_attributes[Fingerprint.LANGUAGE_HTTP] == fp.val_attributes[Fingerprint.LANGUAGE_HTTP]

    def hasSameAcceptHttp(self, fp):
        return self.val_attributes[Fingerprint.ACCEPT_HTTP] == fp.val_attributes[Fingerprint.ACCEPT_HTTP]

    def hasSameHostHttp(self, fp):
        return self.val_attributes[Fingerprint.HOST_HTTP] == fp.val_attributes[Fingerprint.HOST_HTTP]

    def hasSameEncodingHttp(self, fp):
        return self.val_attributes[Fingerprint.ENCODING_HTTP] == fp.val_attributes[Fingerprint.ENCODING_HTTP]

    def hasSameUserAgentHttp(self, fp):
        return self.val_attributes[Fingerprint.USER_AGENT_HTTP] == fp.val_attributes[Fingerprint.USER_AGENT_HTTP]

    def hasSameOrderHttp(self, fp):
        return self.val_attributes[Fingerprint.ORDER_HTTP] == fp.val_attributes[Fingerprint.ORDER_HTTP]

    def hasSameConnectionHttp(self, fp):
        return self.val_attributes[Fingerprint.CONNECTION_HTTP] == fp.val_attributes[Fingerprint.CONNECTION_HTTP]

    def hasSamePlugins(self, fp):
        return self.val_attributes[Fingerprint.PLUGINS_JS] == fp.val_attributes[Fingerprint.PLUGINS_JS]

    def hasSameNbPlugins(self, fp):
        return self.val_attributes[Fingerprint.NB_PLUGINS] == fp.val_attributes[Fingerprint.NB_PLUGINS]

    def hasSameFonts(self, fp):
        return self.val_attributes[Fingerprint.FONTS_FLASH] == fp.val_attributes[Fingerprint.FONTS_FLASH]

    def hasSamePlatformFlash(self, fp):
        return self.val_attributes[Fingerprint.PLATFORM_FLASH] == fp.val_attributes[Fingerprint.PLATFORM_FLASH]

    def hasSameLanguageFlash(self, fp):
        return self.val_attributes[Fingerprint.LANGUAGE_FLASH] == fp.val_attributes[Fingerprint.LANGUAGE_FLASH]

    def hasSameResolutionFlash(self, fp):
        return self.val_attributes[Fingerprint.RESOLUTION_FLASH] == fp.val_attributes[Fingerprint.RESOLUTION_FLASH]

    def hasSameNbFonts(self, fp):
        return self.val_attributes[Fingerprint.NB_FONTS] == fp.val_attributes[Fingerprint.NB_FONTS]

    def hasSameCanvasJsHashed(self, fp):
        return self.val_attributes[Fingerprint.CANVAS_JS_HASHED] == fp.val_attributes[Fingerprint.CANVAS_JS_HASHED]

    def hasSamePlatformJs(self, fp):
        return self.val_attributes[Fingerprint.PLATFORM_JS] == fp.val_attributes[Fingerprint.PLATFORM_JS]

    def hasSameSessionJs(self, fp):
        return self.val_attributes[Fingerprint.SESSION_JS] == fp.val_attributes[Fingerprint.SESSION_JS]

    def hasSameAddressHttp(self, fp):
        return self.val_attributes[Fingerprint.ADDRESS_HTTP] == fp.val_attributes[Fingerprint.ADDRESS_HTTP]

    def hasSameDnt(self, fp):
        return self.val_attributes[Fingerprint.DNT_JS] == fp.val_attributes[Fingerprint.DNT_JS]

    def hasSameCookie(self, fp):
        return self.val_attributes[Fingerprint.COOKIES_JS] == fp.val_attributes[Fingerprint.COOKIES_JS]

    def hasSameLocalJs(self, fp):
        return self.val_attributes[Fingerprint.LOCAL_JS] == fp.val_attributes[Fingerprint.LOCAL_JS]

    def hasSameFlashBlocked(self, fp):
        return self.hasFlashBlockedByExtension() == fp.hasFlashBlockedByExtension()

    def hasSameLanguageInconsistency(self, fp):
        if self.val_attributes[Fingerprint.LANGUAGE_INCONSISTENCY] and fp.val_attributes[Fingerprint.LANGUAGE_INCONSISTENCY]:
            return "0"
        elif self.val_attributes[Fingerprint.LANGUAGE_INCONSISTENCY] or fp.val_attributes[Fingerprint.LANGUAGE_INCONSISTENCY]:
            return "1"
        else:
            return "2"

    def hasSamePlatformInconsistency(self, fp):
        if self.val_attributes[Fingerprint.PLATFORM_INCONSISTENCY] and fp.val_attributes[Fingerprint.PLATFORM_INCONSISTENCY]:
            return "0"
        elif self.val_attributes[Fingerprint.PLATFORM_INCONSISTENCY] or fp.val_attributes[Fingerprint.PLATFORM_INCONSISTENCY]:
            return "1"
        else:
            return "2"

    # Compare the current fingerprint with another one (fp)
    # Returns True if the current fingerprint has a highest (or equal) version of browser
    def hasHighestBrowserVersion(self, fp):
        if self.getCounter() > fp.getCounter():
            mostRecent = self
            oldest = fp
        else:
            mostRecent = fp
            oldest = self

        try:
            return mostRecent.val_attributes[Fingerprint.MAJOR_BROWSER_VERSION] >= oldest.val_attributes[Fingerprint.MAJOR_BROWSER_VERSION]
        except:
            return True


    # Returns True if the plugins of the current fingerprint are a subset of another fingerprint fp or the opposite
    # Else, it returns False
    def arePluginsSubset(self, fp):
        pluginsSet1 = set(self.getPlugins())
        pluginsSet2 = set(fp.getPlugins())
        return (pluginsSet1.issubset(pluginsSet2) or pluginsSet2.issubset(pluginsSet1))

    def getNumberDifferentPlugins(self, fp):
        pluginsSet1 = set(self.getPlugins())
        pluginsSet2 = set(fp.getPlugins())
        return max(self.getNumberOfPlugins(), fp.getNumberOfPlugins()) - len(pluginsSet1.intersection(pluginsSet2))

    # Returns True if the fonts of the current fingerprint are a subset of another fingerprint fp or the opposite
    # Else, it returns False
    def areFontsSubset(self, fp):
        fontsSet1 = set(self.getFonts())
        fontsSet2 = set(fp.getFonts())
        return (fontsSet1.issubset(fontsSet2) or fontsSet2.issubset(fontsSet1))

    # return True if 2 fingeprints belong to the same user (based on the id criteria)
    def belongToSameUser(self, fp):
        return self.val_attributes[Fingerprint.ID] == fp.val_attributes[Fingerprint.ID]

    def getId(self):
        return self.val_attributes[Fingerprint.ID]

    def getCounter(self):
        return self.val_attributes[Fingerprint.COUNTER]