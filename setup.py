import setuptools

setuptools.setup(
    name='hg',
    version='0.0.0',
    author='Trevor Manz',
    author_email='trevor.j.manz@gmail.com',
    description='python bindings for higlass',
    packages=setuptools.find_packages(),    
    install_requires=['pydantic'],
)
