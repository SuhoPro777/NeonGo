from setuptools import setup, find_packages

setup(
    name="neongo",
    version="1.0.0",
    description="NeonGo - High-performance runtime, microservice runner, task execution layer.",
    author="Neon Team",
    author_email="dev@neonlib.ai",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
