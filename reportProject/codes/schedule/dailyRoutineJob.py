from codes.controllers.NodeJsServerController import NodeJsServerController


def will_uploadRoutineJob():

    # define server
    serverController = NodeJsServerController()
    # call upload item master
    serverController.uploadMachineItemMaster()
    # call upload HK key project
    serverController.uploadHkKeyProject()
    print('Item Master and HK key project have been updated. ')
