# py_toio_cube

Access test to toio core cube with python3 on Windows

This sample code uses [bleak](https://pypi.org/project/bleak/).


## Quick Start

```
pip install bleak
git clone https://github.com/kaz399/py_toio_cube.git
cd py_toio_cube
python search_cube.py
```


## Notice

**Don't replace** the bluetooth driver to WinUSB.  
[bleak](https://pypi.org/project/bleak/) uses .NET backend on Windows.  
If you had replaced the bluetooth driver to WinUSB already, You have to revert to original driver. ( WinUSB driver is required by [toio.js](https://github.com/toio/toio.js/))


## Reference

[toio Core Cube Specification](https://toio.github.io/toio-spec/)
