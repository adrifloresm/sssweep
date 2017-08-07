#!/usr/bin/env python3

import argparse
import os
import sssweep
import taskrun

def main(args):
  # ========================================================================== #
  # taskrun
  # ========================================================================== #
  # activate log
  fd = None
  if args.log is not None:
    fd = open(args.log, 'w')

  # create a task manager to handle all tasks
  rm = taskrun.ResourceManager(taskrun.CounterResource('cpus', 9999, args.cpus),
                               taskrun.MemoryResource('mem', 9999, args.mem))
  vob = taskrun.VerboseObserver(description=args.verbose, summary=True, log=fd)
  cob = taskrun.FileCleanupObserver()
  tm = taskrun.TaskManager(resource_manager=rm,
                           observers=[vob, cob],
                           failure_mode=taskrun.FailureMode.ACTIVE_CONTINUE)

  # define resource usage
  def get_resources(task_type, config):
    if task_type is 'sim':
      return {'cpus': 1, 'mem': args.simmem}
    else:
      return {'cpus': 1, 'mem': 3}
  # ========================================================================== #
  # Sweeper
  # ========================================================================== #
  """
  Defaults:
  Mandatory:
  supersim_path, settings_path, sslatency_path, out_dir,
  Predefined:
  parse_scalar = None, plot_units = None, ymin = None , ymax = None,
  long_titles = True, plot_style='colon',
  latency_mode = 'Packet', # 'Packet', 'Message', 'Transaction'
  sim = True, parse = True, qplot = True, lplot = True, cplot = True,
  web_viewer = True, get_resources = None
  """
  s = sssweep.Sweeper(args.supersim_path, args.settings_path,
                      args.sslatency_path, args.out_dir,
                      parse_scalar=0.001, plot_units='ns',
                      ymin=0, ymax=500, long_titles=True,
                      plot_style='colon',
                      latency_mode='Message',
                      sim=True, parse=True,
                      qplot=True, lplot=True, cplot=True,
                      web_viewer=True, get_resources=get_resources)

  # ========================================================================== #
  # sweep variables & set commands
  # ========================================================================== #
  a_all = {'A':'a...', 'B':'b...'}
  def set_a_cmd(a, config):
    cmd = ('{0}'.format(a))
    return cmd

  b_all = ['','']
  def set_b_cmd(b, config):
    cmd = '...'
    return cmd

  # loads
  def set_load_cmd(l, config):
    cmd = ['','']
    return cmd

  # ========================================================================== #
  # add variables
  # ========================================================================== #
  # addVariable(name, shortName, values, setCommand, compare=True)
  s.add_variable('A_variable', 'A', a_all, set_a_cmd, compare=True)
  s.add_variable('B_variable', 'B', b_all, set_b_cmd, compare=True)

  # add loads
  # addLoads(name, shortName, start, stop, step, setCommand)
  s.add_loads('Load', 'l', args.start, args.stop, args.step, set_load_cmd)
  # ========================================================================== #
  # run tasks
  # ========================================================================== #
  # generate all tasks
  s.create_tasks(tm)

  # run the tasks
  tm.run_tasks()

# =========================================================================== #
# input arguments
# =========================================================================== #
if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('supersim_path',
                  help='location of supersim bin')
  ap.add_argument('settings_path',
                  help='the JSON settings file')
  ap.add_argument('sslatency_path',
                  help='location of sslatency bin')
  ap.add_argument('out_dir',
                  help='location of output files directory')

  ap.add_argument('start', type=int,
                  help='load start')
  ap.add_argument('stop', type=int,
                  help='load stop')
  ap.add_argument('step', type=int,
                  help='load step')

  ap.add_argument('-c', '--cpus', type=int, default=os.cpu_count(),
                  help='maximum number of cpus to use during run')
  ap.add_argument('-m', '--mem', type=float,
                  default=taskrun.MemoryResource.current_available_memory_gib(),
                  help='maximum amount of memory to use during run')
  ap.add_argument('-s', '--simmem', type=float, default=10.0,
                  help='amount of memory for SuperSim simulation tasks')
  ap.add_argument('-v', '--verbose', action='store_true',
                  help='show all commands')
  ap.add_argument('-l', '--log', type=str, default=None,
                  help='log file for Taskrun Observer')
  args = ap.parse_args()
  exit(main(args))
