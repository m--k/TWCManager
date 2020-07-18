# Read the currently exported energy from a power meter that is connected to a SolarEdge inverter
# You must enable ModBusTCP in your inverter, using the Solaredge SetApp

class SolarEdgeMeter:

    import re
    import time
    import solaredge_modbus

#todo variablen prüfen
    cacheTime = 10    # wait 10 seconds between modbus requests
    config = None
    configConfig = None
    configSolarEdgeMeter = None
    consumedW = 0
    debugLevel = 0
    fetchFailed = False
    generatedW = 0
    #importW = 0
    exportedW = 0
    lastFetch = 0
    master = None
    serverIP = None
    serverPort = 1502
    status = False
    timeout = 10
    #voltage = 0
    inverter = None   #SolarEdge inverter
    meter1 = None     #SolarEdge power meter
	

    def __init__(self, master):
        self.debugLog(1, "__init__() called")
        print("SolarEdgeMeter: __init__() called") 
        self.master = master
        self.config = master.config
        try:
            self.configConfig = self.config["config"]
        except KeyError:
            self.configConfig = {}
        try:
            self.configSolarEdgeMeter = self.config["sources"]["SolarEdgeMeter"]
        except KeyError:
            self.configSolarEdgeMeter = {}
        self.debugLevel = self.configConfig.get("debugLevel", 0)
        self.status = self.configSolarEdgeMeter.get("enabled", False)
        self.serverIP = self.configSolarEdgeMeter.get("serverIP", None)
        self.debugLog(1, f"serverIP:  {self.serverIP}")
        self.serverPort = self.configSolarEdgeMeter.get("serverPort", "1502")

        # Unload if this module is disabled or misconfigured
        if ((not self.status) or (not self.serverIP)
           or (int(self.serverPort) < 1)):
          self.master.releaseModule("lib.TWCManager.EMS","SolarEdgeMeter");
		  
		##todo try...catch
        import solaredge_modbus
        self.inverter = solaredge_modbus.Inverter(host="192.168.178.81", port=self.serverPort)
        self.inverter.meters()
        self.meter1 = self.inverter.meters()["Meter1"]


    def debugLog(self, minlevel, message):
        if self.debugLevel >= minlevel:
            print("SolarEdgeMeter: (" + str(minlevel) + ") " + message)

    def getConsumption(self):
        print("SolarEdgeMeter: getConsumption() called")
        if not self.status:
            self.debugLog(1, "SolarEdgeMeter EMS Module Disabled. Skipping getConsumption")
            return 0

        # Perform updates if necessary
        self.update()

        # Return generation value
        return float(self.consumedW)
        
        
    def getGeneration(self):
        if not self.status:
            self.debugLog(1, "SolarEdgeMeter EMS Module Disabled. Skipping getGeneration")
            return 0

        # Perform updates if necessary
        self.update()

        # Return generation value
        return float(self.generatedW)

  
    def update(self):
        if (int(self.time.time()) - self.lastFetch) > self.cacheTime:
            # Cache has expired. Fetch values from modbus
            try:
                # read the generated solar power from the inverter
                gen_dict = self.inverter.read("power_ac")   # returns a dict with one entry, not a value!
                gen = gen_dict['power_ac']             # get the value from the dict
                # read the scale factor for the exported power from the meter
                gen_scale_dict = self.inverter.read("power_ac_scale")   #returns a dict with one entry, not a value!
                gen_scale = gen_scale_dict['power_ac_scale']       #get the value from the dict

                self.generatedW = gen * (10 ** gen_scale)
                self.debugLog(1, f"Erzeugung:  {self.generatedW}")
                
                # read the exported power from the meter
                exp_dict = self.meter1.read("power")   # returns a dict with one entry, not a value!
                exp = exp_dict['power']             # get the value from the dict
                # read the scale factor for the exported power from the meter
                exp_scale_dict = self.meter1.read("power_scale")   #returns a dict with one entry, not a value!
                exp_scale = exp_scale_dict['power_scale']       #get the value from the dict

                self.exportedW = exp * (10 ** exp_scale)
                self.debugLog(1, f"Einspeisung:  {self.exportedW}")
                
                self.consumedW = self.generatedW - self.exportedW
                self.debugLog(1, f"Verbrauch:  {self.consumedW}")
               
                
                
                self.lastFetch = int(self.time.time())
            except:
                self.generatedW = 0
                self.consumedW = 0
                self.debugLog(1, "Exception: Failed to read values from modbus from SolarEdgeMeter")
                return True
        else:
            # Cache time has not elapsed since last fetch, serve from cache.
            return False
