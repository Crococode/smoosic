from distutils.core import setup
from glob import glob
import py2exe
import sys

sys.path.append("C:\\Users\\Hugo\\Desktop\\Code\\CMake\\bin")

#data_files = [("Microsoft.VC90.CRT", glob(r'C:\Users\Hugo\Desktop\Code\CMake\bin\*.*'))]
#data_files.append([("Numpy", [glob(r'C:\Python27\lib\site-packages\numpy\linalg\_umath_linalg.pyd'),glob(r'C:\Python27\lib\site-packages\numpy\fft\fftpack_lite.pyd')])])

setup(
    windows = [{'script': "pb_qt.py"}],
  # console=['pb_qt.py'],
  #  data_files=data_files,
    options={
            'py2exe': 
            {
                'includes': ['lxml.etree', 'lxml._elementpath', 'yaafelib', 'yaafelib.yaafe_extensions.yaafefeatures', 'sip'],
                'bundle_files': 1, 'compressed': True
            }
        },
    zipfile = None
)

