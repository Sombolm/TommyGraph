from Backend.Tomograph import Tomograph

tomograph = Tomograph()
tomograph.run("../ExampleDICOM/Kropka.dcm", 10, 180, 180, True, None,
              None, False, {},"../ExampleImages/Shepp_logan.jpg")
