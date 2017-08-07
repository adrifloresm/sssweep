# sssweep - Easy Simulations with sssweep

The sssweep tool is intended to aid analysis of interconnect networks performed with the [SuperSim][] simulator. When performing network analysis there are immense number of variables to study, such as multiple workloads, network configurations, injection rates, routing algorithms, among others. These studies lead to thousands of results or plots to analyse and strenuous simulation setup. Sssweep solves these two problems by enabling a flexible and easy-to-use system to configure, run, parse and plot simulations with any number of variables and configurations, as well as auto-creating a web-viewer to view and study the results from your simulation that is tailored to the specific parameters of your simulations.
To understand sssweep's power, we will do a detailed walk through the components of sssweep with a skeleton running script.

## How to run sssweep
For this tutorial we provide a [skeleton][] script provides a flexible setup where you can input the path to your SuperSim, SSLatency binaries, as well as the load settings.
To run the sssweep simulations, using the setup of the skeleton script, you can use the following command and modify the paths to your [SuperSim][] and [SSLatency][] binary and the name of the output folder.

Run command
```sh
./skeleton_script.py [supersim bin] [JSON settings] [sslatency bin] [out dir] [start] [stop] [step]
```
Here is the list of input arguments used by skeleton_script.py

Mandatory:
1. 'supersimPath' = 'location of SuperSim bin'
2. 'settingsPath' = 'the JSON settings file'
3. 'sslatencyPath'= 'location of sslatency bin'
4. 'outdir'= 'location of output files directory'
5. 'start'='load start'
6. 'stop'= 'load stop'
7. 'step'='load step'

Optional:
- '-c', '--cpus','maximum number of cpus to use during run'
- '-m', '--mem', 'maximum amount of memory to use during run'
- '-s', '--simmem','amount of memory for SuperSim simulation tasks'
- '-v', '--verbose','show all commands'
- '-l', '--log', 'log file for TaskRun Observer'

## Web viewer

After the simulation has been run and successfully completed we can launch the web plot viewer to analyse the results.

First you need to access the folder where the output files of your simulation reside.

After you will see 4 different folders: data/, web_viewer/, logs/ and plots/. Because our web plot viewer requires access to the plots folder we will launch the plot viewer from outside the web_viewer folder.

Now you are ready to launch the web plot viewer by running the following from the command line:
```sh
python3 -m http.server 8888
```

This will run a local python server. Now you can open a web browser to view the results. If you are running the web browser in the same computer as the simulations, then type the following address:
```
http://localhost:8888/web_viewer/plots.html
```
To access the web plot viewer from an external computer to where your files reside, you must know the IP of the computer where the files reside and replace `localhost` with that IP address.

Once in your web-browser, on the left of the web plot viewer, you will see different drop-downs that are created based on your simulation configuration. You can first select between three plot types: lplot, qplot and cplot. Note, cplot is only activated if it is enabled on the sweeper object and there exist compare variables with more than one setting, e.g. routing algorithm: oblivious and adaptive.
After selecting a plot type, the appropriate drop-down selectors will appear in correspondence to the existing plot type. Note, variables with only one option are not displayed and are automatically filled in the filename.
The filename is displayed at the bottom of the selectors, if the filename is red, the requested figure does not exist. Once all the options are selected the plot is displayed automatically.


## How does sssweep work - walk through
Now let's walk through the [skeleton][] script to get a better understanding of how sssweep works.

```sh
emacs skeleton_script.py
```

### TaskRun and resources
First, we setup [TaskRun][], we create and configure the task manager, and define a function to get the computational resources.
Here, the two important input arguments are the  `args.simmem` and the `args.log`. The `args.simmem` defines the amount of memory to use for simulations during a run (the default value is set to 10 G). In case you want to debug [TaskRun][], the `args.log` will print the output of the verbose observer in TaskRun to the file specified in the `args.log` argument.

### Sweeper

In this section we create the sweeper object as follows:

```python
s = sssweep.Sweeper(args.supersim_path, args.settings_path,
                      args.sslatency_path, args.out_dir,
                      parse_scalar=0.001, plot_units='ns',
                      ymin=0, ymax=500, long_titles=True,
                      plot_style='colon',
                      latency_mode='Message',
                      sim=True, parse=True,
                      qplot=True, lplot=True, cplot=True,
                      web_viewer=True, get_resources=get_resources)
```

This is the list of input arguments for Sweeper:

Mandatory:
* supersim_path, settings_path, sslatency_path, out_dir,
Predefined:
* parse_scalar=None, plot_units=None, ymin=None, ymax=None,
* long_titles=True, plot_style='colon',
* latency_mode='Packet', # 'Packet', 'Message', 'Transaction'
* sim=True, parse=True,
* qplot=True, lplot=True, cplot=True,
* web_viewer=True,
* get_resources=None

First we set the **mandatory arguments** that are the input files and output directory in the following order:
```python
supersim_path, settings_path, sslatency_path, out_dir
```

Next we define the **plot settings** using the previously set variables of ymin, ymax, as well as the parsing unit and units for latency plot.
```python
parse_scalar=None, plot_units=None, ymin=None, ymax=None
```

Additional plot settings exist for plot titles. In sssweep, you can enable long titles which use the full length of the variable name or you can enable short titles (`long_titles=False`) to use the shortnames on the titles. As well with the variable plot_style you have two options for dividers "colon" or "equal". You can use any combination of these two settings of `long_titles` and `plot_style` to define you preferred title format.

Here are some examples:
- [_long_titles=True, plot_style='colon'_] Load vs. Latency (TrafficPattern: UR, RoutingAlgorithm: AD)
- [_long_titles=True, plot_style='equal'_] Load vs. Latency (TrafficPattern=UR RoutingAlgorithm=AD)
- [_long_titles=False, plot_style='colon'_] LvL (TP: UR, RA: AD)
- [_long_titles=False, plot_style='equal'_] LvL (TP=UR RA=AD)

Next, you can define the **latency mode** with either 'Packet', 'Message' or 'Transaction' latency data:
```python
latency_mode='Packet', # 'Packet', 'Message', 'Transaction'
```

Further, sssweep gives you the flexability to enable or disable the execution of the **simulation, parsing, lplot, cplot, qplot or web_viewer**.
```python
sim=True, parse=True, qplot=True, lplot=True, cplot=True, web_viewer=True
```

The last argument gets memory resources for the simulation, which needs a function pointer to the resources function defined in the TaskRun section.
```python
 get_resources=get_resources
```

### sweep variables and set commands

A key benefit to sssweep is the easiness to add multiple simulation variables. In the next section of the [skeleton][] code, the simulation variables are created along with their associated function that defines the commands to set the variables in the JSON file.

Simulation variables can be defined in a dictionary format or a list of strings. Note that when variables are defined in dictionary format the dictionary key is used in the filename.
``` python
routing_algorithms = {'OB':'oblivious', 'AD':'adaptive'}
```
or
``` python
routing_algorithms = ['oblivious', 'adaptive']
```

Set commands can be provided in a single string format or an array of strings. See these sudo-examples:
``` python
cmd = ['workload.applications[0].blast_terminal... ',
       'workload.applications[0].blast_terminal.enable_responses=bool=false ']
```
or
``` python
cmd = ('workload.applications[0].blast_terminal.request_injection_rate=float={0} '
           'workload.applications[0].blast_terminal.enable_responses=bool=false '
           .format(parse_scalar if l == '0.00' else l))
```

The load variable is defined differently from the other simulation variables. We do not need to define the load variable ourselves, this is taken care of by the sweeper with the input arguments start, stop and step. You only need to define the function to set the load command for the JSON file. Here is an example, note the command may be out-of-date with future SuperSim releases.

```python
 # loads
  def set_load_cmd(l, var):
    cmd = ('workload.applications[0].blast_terminal.request_injection_rate=float={0} '
           'workload.applications[0].blast_terminal.enable_responses=bool=false '
           .format(parseScalar if l == '0.00' else l))
    return cmd
```

All the set command functions use two input arguments. The first argument stands for one instance of the sweep variable, e.g. 'UR': 'uniform_random' and the second 'config' (generated by the sweeper) contains all the sweep variables for the current simulation run. The config is provided in case the set command requires to use the value of any of the other sweep variables of the current instance of the simulation.

### add variables

Now that all the simulation variables and their respective set command functions have been defined, we can add the variables to the sweeper object.
Note, a variable can be defined above but won't be considered for simulation until it is added to the sweeper object. To add a variable we use the following command:
```python
  # SweeperObjectName.addVariable(name, shortName, values, setCommand, compare=True)
```

The function `addVariable` takes 4 input arguments. First the `name` of the variable which is considered to be the long format of the variable name, the second argument is `shortName` which is the abbreviated name of the variable used by the cplot filenames and tasks ids, third is the set command function for this specific variables. The last argument is the `compare` Boolean flag, that specifies if the variable will be considered in compare plots if the cplot type is enabled. The default value of the compare flag is set to True.

Next, we add the load variable to our simulation.
``` python
s.addLoads(name, shortName, start, stop, step, setCommand)
```
Note that the add load variable command (`addLoads`) is different from the previous add variable command. The addLoads function takes as input the following arguments: `name, shortName, start, stop, step, setCommand` where name and short name represent the variable name in long and short format respectively. The start, stop and step give the load parameters to the sweeper object to generate the simulation loads. Finally the setCommand is the function name to the setting command function previously defined.

### run tasks

Now that all the variables have been defined and added to our sweeper object, we can auto-generate and run the tasks. We first tell our sweeper object to create the tasks using the predefined task manager `tm` and after we set the task manager to run these tasks. This is performed by the following code.

```python
  # generate all tasks
  s.createTasks(tm)

  # run the tasks
  tm.run_tasks()
```
This concludes the walkthrough of sssweep, if you have any questions or recommendations please let us know.

[TaskRun]: https://github.com/nicmcd/taskrun
[SSLatency]: https://github.com/nicmcd/sslatency
[SSPlot]: https://github.com/nicmcd/ssplot
[skeleton]: skeleton_script.py
[SuperSim]: https://github.com/HewlettPackard/supersim
