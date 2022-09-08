from codes.controllers.ServerController import ServerController


def will_uploadRoutineJob():
    # define server
    serverController = ServerController()
    # call upload item master
    serverController.uploadMachineItemMaster()
    # call upload HK key project
    serverController.uploadHkKeyProject()
    print('Item Master and HK key project have been updated. ')
