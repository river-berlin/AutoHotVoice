from setuptools import setup, find_packages

setup(
    name="autohotvoice",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "keyboard",
        "httpx",
        "pyautogui",
        "deepgram-sdk",
    ],
)