# sssweep

## Summary
sssweep is a flexible and easy-to-use python package to automatically perform supersim simulations with one to many sweeping variables. sssweep allows the user to easily add as many simulation variables as wanted, where each simulation variable can have one or many values.

As the number of simulations increase so does the number of plots generated, sssweep introduces a convenient feature to help you visualize results, the sssweep webviewer. The sssweep webviewer is automatically generated based on your simulation parameters. The webviewer lets you share your results from the computer where the simulation was performed to other computers and with other peers, by only launching a local python server, removing the need to copy images across computers and email attachements.

## Install
sssweep requires [TaskRun](https://github.com/nicmcd/taskrun) and [SSplot](https://github.com/nicmcd/ssplot) in addition to [SuperSim](https://github.com/HewlettPackard/supersim).

#### Install globally:
```
sudo pip3 install git+https://github.com/nicmcd/sssweep.git
```
#### Install locally:
```
pip3 install --user git+https://github.com/nicmcd/sssweep.git
```
### Source installation

#### Install globally:
```
sudo python3 setup.py install
```
#### Install locally:
```
python3 setup.py install --user
```

## Uninstall

Uninstall global installation:
```
sudo pip3 uninstall sssweep
```
Uninstall local installation:
```
pip3 uninstall sssweep
```
## Tutorial

See tutorial in [docs](docs/README.md) folder
