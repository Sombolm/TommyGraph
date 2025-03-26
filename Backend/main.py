from Backend.Tomograph import Tomograph

tomograph = Tomograph()
tomograph.run("../ExampleImages/Shepp_logan.jpg", 20, 180, 180, True, None,
              True, dict(
    PatientName='Test',
    PatientID='001',
    ImageComments='Comment',
    StudyDate='20250321',
), "../OutputImages/test.jpg")
