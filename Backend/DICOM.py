from pydicom import dcmread

class DICOM:
    def readDicomFile(self, path):
        dicom = dcmread(path)

        keys = dicom.dir()
        meta = {x: getattr(dicom, x) for x in keys}

        image = dicom.pixel_array

        return image, meta

    #TODO implement writing to DICOM
    def saveAsDicomFile(self, path, image, meta):
        dicom = dcmread(path)

        for key in meta:
            setattr(dicom, key, meta[key])

        dicom.PixelData = image.tobytes()

        dicom.save_as(path)