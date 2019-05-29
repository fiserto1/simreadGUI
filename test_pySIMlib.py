from pySIMlib import pySIMlib

def testReadSIM(comport):
    sim = pySIMlib(True)

    #sim.openSession("/dev/ttyUSB0")
    sim.openSession(comport)

    print("\nPIN")
    pin_e, pin_t = sim.getPINinfo()
    print("EN: %d TR: %d" % sim.getPINinfo())

    #sim.enPIN("0123")
    #print("EN: %d TR: %d" % sim.getPINinfo()
    #sim.chgPIN("0123", "2973")
    #print("EN: %d TR: %d" % sim.getPINinfo()
    #sim.disPIN("2973")
    #print("EN: %d TR: %d" % sim.getPINinfo()

    print("\nMandatory Fields")
    print("\nICCID")
    print(sim.getICCID())

    print("\nLP")
    print(sim.getLP())

    print("\nIMSI")
    print(sim.getIMSI())

    print("\nKC")
    print(sim.getKC())

    print("\nHPLMN")
    print(sim.getHPLMN())

    print("\nSST")
    print(sim.getSST())

    print("\nBCCH")
    print(sim.getBCCH())

    print("\nACC")
    print(sim.getACC())

    print("\nFPLMN")
    print(sim.getFPLMN())

    print("\nLOCI")
    print(sim.getLOCI())

    print("\nAD")
    print(sim.getAD())

    print("\nPhase")
    print(sim.getPhase())

    print("\nNUMBERS")

    print("\nADN")
    recNum, recLen, nameLen =  sim.getNumInfo (sim.FILE_EF_ADN)
    print(sim.getNumInfo (sim.FILE_EF_ADN))
    print(sim.getNums (sim.FILE_EF_ADN))
    print(sim.setNum (sim.FILE_EF_ADN, 1, recLen, nameLen, "Peter", "031611816"))
    print(sim.getNum (sim.FILE_EF_ADN, 1, recLen, nameLen))

    print("\nFDN")
    recNum, recLen, nameLen =  sim.getNumInfo (sim.FILE_EF_FDN)
    print(sim.getNumInfo (sim.FILE_EF_FDN))
    print(sim.getNums (sim.FILE_EF_FDN))
    print(sim.getNum (sim.FILE_EF_FDN, 1, recLen, nameLen))

    print("\nLND")
    recNum, recLen, nameLen =  sim.getNumInfo (sim.FILE_EF_LND)
    print(sim.getNumInfo (sim.FILE_EF_LND))
    print(sim.getNums (sim.FILE_EF_LND))
    print(sim.setNum (sim.FILE_EF_LND, 1, recLen, nameLen, "Vera", "031681716"))
    print(sim.getNums (sim.FILE_EF_LND))


    print("\nSMS")
    recNum, recLen = sim.getSMSinfo()
    print(sim.getSMSinfo())
    print(sim.getSMSs())
    print(sim.getSMS(1, recLen))

if __name__ == "__main__":
    testReadSIM("COM3")