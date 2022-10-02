from pysnmp.entity.rfc3413.oneliner import cmdgen

def get_par(agent,oid_mib,password = 'password'):
    oid,mib = oid_mib.split(" ")
    #print(oid,mib,sep=' - ')
    errorIndication, errorStatus, errorIndex, \
                     BindTable = cmdgen.CommandGenerator().nextCmd(
        cmdgen.CommunityData(password),
        cmdgen.UdpTransportTarget((agent, 161)),
        (oid))
    #print(errorIndication, errorStatus,errorIndex,sep=", ")
    if errorIndication != None:
        return None
    for BindRow in BindTable:
        for name, val in BindRow:
            if mib!= name.prettyPrint():
                continue
            return val.prettyPrint()
    return None
            
with open('seq_num.txt','r') as ff:
    listPar = ff.read().splitlines()

for ss in listPar:
    print(get_par('192.168.110.141',ss))
