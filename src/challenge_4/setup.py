from setuptools import setup

package_name = "challenge_4"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="usuario",
    maintainer_email="barajas@uji.es",
    description="ROS 2 node for challenge 4",
    license="Apache-2.0",
    entry_points={
        "console_scripts": ["challenge_4 = challenge_4.node:main"],
    },
)
