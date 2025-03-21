from Backend.Tomograph import Tomograph

tomograph = Tomograph()
tomograph.run("../ExampleImages/Shepp_logan.jpg", 10, 180, 180, False, None,
              False, dict(
    PatientName='Test',
    PatientID='001',
    ImageComments='Comment',
    StudyDate='20250321',
), "../OutputImages/test.jpg")
