from Backend.Tomograph import Tomograph

tomograph = Tomograph()
tomograph.run("../ExampleImages/Kolo.jpg", 10, 180, 180, True, None,
              False, dict(
    PatientName='Test',
    PatientID='001',
    ImageComments='Comment',
    StudyDate='20250321',
), "../ExampleDICOM/test.jpg")
