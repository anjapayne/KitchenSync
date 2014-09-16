from distutils.core import setup

setup(
    name='KitchenSync',
    version='1.0',
    packages=['audiochannelsync',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    install_requires = ["scipy", "numpy", "matplotlib", "wave"],
    long_description=open('README.rst').read(),
    scripts=["audiochannelsync/__main__.py"]
    description="Tool to syncronise video to recorded dataset using common signal recorded within a dataset and the audio track."
)
