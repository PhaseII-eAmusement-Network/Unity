import os
import shutil
from setuptools import Command, setup

class CleanExtCommand(Command):
    description = 'Clean all compiled python extensions from the current directory.'

    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        print("Removing build directory...")
        shutil.rmtree(os.path.abspath("build/"), ignore_errors=True)
        for dirname, __, fileList in os.walk(os.path.abspath(".")):
            for filename in fileList:
                if filename[-3:] == ".so":
                    fullname = os.path.join(dirname, filename)
                    print(f"Removing {fullname}")
                    os.remove(fullname)


setup(
    name='Unity Backend API',
    version='0.1',
    description="Webhook host server and developer network",
    author='PhaseII Team',
    license='Apache 2.0',
    packages=[
        # Core packages
        'api',
        
        # Wrapper scripts, utilities and associated code.
        'api.utils',

    ],
    install_requires=[
        req for req in open('requirements.txt').read().split('\n') if len(req) > 0
    ],
    cmdclass={
        'clean_ext': CleanExtCommand,
    },
    include_package_data=True,
    zip_safe=False,
)
