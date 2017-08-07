"""
 * Copyright (c) 2012-2017, Nic McDonald and Adriana Flores
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import copy
import ssplot
import taskrun
from .web_viewer_gen import *

class Sweeper(object):

  def __init__(self, supersim_path, settings_path, sslatency_path, out_dir,
               parse_scalar=None, plot_units=None, ymin=None, ymax=None,
               long_titles=True, plot_style='colon',
               latency_mode='Packet',
               sim=True, parse=True,
               qplot=True, lplot=True, cplot=True,
               web_viewer=True,
               get_resources=None):
    """
    Constructs a Sweeper object

    Args:
      supersim_path       : path to supersim bin
      settings_path       : path to settings file
      sslatency_path      : path to sslatency bin
      out_dir             : location of output files directory
      parse_scalar        : Latency sacalar for parsing
      plot_units          : unit of latency (ns)
      ymin, ymax          : ylim for plots
      long_titles         : enable full name on plot titles
      plot_style          : style of plot titles (colon : or equal = )
      latency_mode        : 'packets', 'messages', 'transactions'
      sim, parse          : bools to enable/disable sim and parsing
      qplot, lplot, cplot : bools to enable/disable plots (quad, load, compare)
      web_viewer          : bool to enable/disable web viewer generation
      get_resources       : pointer to set resource function for tasks
    """
    # paths
    self._supersim_path = os.path.abspath(os.path.expanduser(supersim_path)) # '../supersim/bin/supersim'
    self._out_dir = os.path.abspath(os.path.expanduser(out_dir)) # where to save files
    self._settings_path = os.path.abspath(os.path.expanduser(settings_path)) # './settings.json'
    self._sslatency_path = os.path.abspath(os.path.expanduser(sslatency_path)) # '~/ssdev/sslatency/bin/sslatency'

    # plot settings
    self._parse_scalar = parse_scalar # 0.001
    self._plot_units = plot_units # 'ns'
    self._ymin = ymin
    self._ymax = ymax
    self._long_titles = long_titles # long names for plot titles
    self._plot_style = plot_style # colon, equal
    self._latency_mode = latency_mode # 'packet', 'message', 'transaction'

    # task activation
    self._sim = sim
    self._parse = parse
    self._qplot = qplot
    self._lplot = lplot
    self._cplot = cplot
    self._web_viewer = web_viewer
    self._get_resources = get_resources

    # load sweep values
    self._start = None
    self._stop = None
    self._step = None

    self._variables = []
    self._created = False
    self._load_variable = None
    self._load_name = None

    # variables for javascript
    self._id_cmp = "Cmp"
    self._id_lat_dist = "LatDist"
    self._comp_var_count = 0

    # store tasks
    self._sim_tasks = {}
    self._parse_tasks = {}

    # ensure the settings file exists
    if not os.path.isfile(self._settings_path):
      self._error('{0} does not exist'.format(self._settings_path))

    # ensure the supersim bin exists
    if not os.path.isfile(self._supersim_path):
      self._error('{0} does not exist'.format(self._supersim_path))

    # ensure the sslatency bin exists
    if not os.path.isfile(self._sslatency_path):
      self._error('{0} does not exist'.format(self._sslatency_path))

    # ensure outdir exists, if not make it
    if not os.path.isdir(self._out_dir):
      try:
        os.mkdir(self._out_dir)
      except:
        self._error('couldn\'t create {0}'.format(self._out_dir))

    # create subfolders
    # data
    data_f = os.path.join(self._out_dir, 'data/')
    if not os.path.isdir(data_f):
      try:
        os.mkdir(data_f)
      except:
        self._error('couldn\'t create {0}'.format(data_f))
    # logs
    logs_f = os.path.join(self._out_dir, 'logs/')
    if not os.path.isdir(logs_f):
      try:
        os.mkdir(logs_f)
      except:
        self._error('couldn\'t create {0}'.format(logs_f))

    # plots
    plots_f = os.path.join(self._out_dir, 'plots/')
    if not os.path.isdir(plots_f):
      try:
        os.mkdir(plots_f)
      except:
        self._error('couldn\'t create {0}'.format(plots_f))
    # web_viewer
    web_viewer_f = os.path.join(self._out_dir, 'web_viewer/')
    if not os.path.isdir(web_viewer_f):
      try:
        os.mkdir(web_viewer_f)
      except:
        self._error('couldn\'t create {0}'.format(web_viewer_f))

  def add_loads(self, name, short_name, start, stop, step, set_command):
    """
    This creates and adds the load sweep variable to _load_variable

    Args:
      name              : name of sweep variable
      shortname         : acronym of sweep variable for filename
      start, stop, step : load sweep start stop and step
      set_command       : pointer to command function
    """
    # build the variable
    loads = ['{0:.02f}'.format(x_values/100)
             for x_values in range(start, stop+1, step)]
    assert len(loads) > 0
    lconfig = {'name': name, 'short_name': short_name, 'values': list(loads),
               'command': set_command, 'compare' : False, 'values_dic': None}
    # add the variables
    self._load_variable = lconfig
    self._load_name = name
    self._start = start
    self._stop = stop
    self._step = step

  def add_variable(self, name, short_name, values, set_command, compare=True):
    """
    This adds a sweep variable to the config variable

    Args:
      name          : name of sweep variable
      short_name     : acronym of sweep variable for filename
      values        : values of variable to sweep through
      set_command    : pointer to command function
      compare       : should this variable be compared in cplot
    """
    # checks to enable dict format for web display
    if isinstance(values, dict):
      dictvals = values
    else:
      dictvals = None
    # check more than 1 value was given for variable
    assert len(values) > 0
    # build the variable
    configall = {'name': name, 'short_name': short_name, 'values': list(values),
                 'command': set_command, 'compare': compare,
                 'values_dic': dictvals}
    # add the variable
    self._variables.append(configall)

  def _dim_iter(self, do_vars=None, dont=None):
    """
    This function creates the config files with the permutations of the sweep
    variables

    Args:
      do_vars           : variables to iterate through
      dont         : variables to remove from iteration
    """

    tmp_vars = []
    # All variables
    if do_vars is None:
      tmp_vars = copy.deepcopy(self._variables) #Adds all
    else:
      for var in copy.deepcopy(self._variables):
        if var['name'] in do_vars: # add only dos
          tmp_vars.append(var)

    # remove variables
    vars_all = []
    for var in tmp_vars:
      if dont is None or var['name'] not in dont:
        vars_all.append(var) # add only variables not in dont

    # reverse the order
    vars_all = list(reversed(vars_all))

    # find value lengths
    widths = []
    for var in vars_all:
      widths.append(len(var['values']))

    # find top non-single value variable
    top_non_one = None
    for dim in reversed(range(len(widths))):
      if widths[dim] is not 1:
        top_non_one = dim
        break

    # generate all indices
    cur = [0] * len(widths)
    more = True
    while more:
      # yield the configuration
      config = []
      for dim in reversed(range(len(cur))):
        variable = vars_all[dim]
        config.append({
          'name': variable['name'],
          'short_name': variable['short_name'],
          'value': variable['values'][cur[dim]],
          'command': variable['command'],
          'compare': variable['compare']
        })
      yield config

      # detect only one config
      if top_non_one is None:
        more = False
        break

      # advance the generator
      for dim in range(len(widths)):
        if cur[dim] == widths[dim] - 1:
          if dim == top_non_one:
            more = False
            break
          else:
            cur[dim] = 0

        else:
          cur[dim] += 1
          break

  def _error(self, msg, code=-1):
    if msg:
      print('ERROR: {0}'.format(msg))
    exit(code)

  def _make_id(self, config, extra=None):
    """
    This creates id for task

    Args:
      config   : input config to iterate
      extra    : extra values to append at the end (list or string)
    """
    values = [y_var['value'] for y_var in config]
    if extra:
      if isinstance(extra, str):
        values.append(extra)
      elif isinstance(extra, list):
        values.extend(extra)
      else:
        assert False
    return '_'.join([str(x_values) for x_values in values])

  def _make_title(self, config, plot_type, cvar=None, lat_dist=None):
    """
    This creates titles for plots
    # qplot
     Latency (TrafficPattern: UR, RoutingAlgorithm: AD, Load: 0.56)
     Lat (TP: UR, RA: AD, LD: 0.56)
     Lat (TP=UR RA=AD LD=0.56)

    # lplots
     Load vs. Latency (TrafficPattern: UR, RoutingAlgorithm: AD)
     LvL (TP: UR, RA: AD)

    # cplots
     RoutingAlgorithm Comparison (TrafficPattern: UR [Mean])
     RA Cmp (TP: UR [Mean])
    """

    if self._plot_style is 'colon':
      separ = ': '
      delim = ', '
    else:
      separ = '='
      delim = ' '

    #tuples
    name_values = []
    for y_values in config:
      if self._long_titles:
        name_values.append((y_values['name'], str(y_values['value'])))
      else:
        name_values.append((y_values['short_name'], str(y_values['value'])))

    #format
    title = ''
    # name values
    for idx, x_values in enumerate(name_values):
      tmp = separ.join(x_values)
      if idx != len(name_values)-1:
        title += tmp + delim
      else:
        title += tmp
    # qplot
    if plot_type == 'qplot':
      if self._long_titles:
        title = '"Latency ({0})"'.format(title)
      else:
        title = '"Lat ({0})"'.format(title)
    #lplot
    if plot_type == 'lplot':
      if self._long_titles:
        title = '"Load vs. Latency ({0})"'.format(title)
      else:
        title = '"LvL ({0})"'.format(title)
    #cplot
    if plot_type == 'cplot':
      if self._long_titles:
        title = '"{0} Comparison ({1} [{2}])"'.format(cvar['name'], title, lat_dist)
      else:
        title = '"{0} Cmp ({1} [{2}])"'.format(cvar['short_name'], title, lat_dist)
    return title

  def _create_config(self, *args):
    """
    This creates ordered config from multiple sub-configs

    Args:
      *   : configs to combine
    """
    # vars to return
    combined = []
    for var in copy.deepcopy(self._variables):
      for config in args:
        found = False
        for var2 in config:
          if var2['name'] == var['name']:
            found = True
            combined.append(copy.deepcopy(var2))
            break
        if found:
          break
    return combined

  def _cmd_clean(self, cmd):
    """
    This adds leading space to input commands

    Args:
      cmd   : cmd to clean (str or array)
    """
    assert cmd is not None, 'You must return a command modifier'
    if isinstance(cmd, str):
      cmd = [cmd]
    clean = ' '+' '.join([str(x_values) for x_values in [y for y in cmd]])
    return clean

  def _get_files(self, id_task):
    """
    This creates file names for a given id_task

    Args:
      id_task   : id_task to generate files for
    """
    dir_var = self._out_dir
    return {
      'messages_mpf'  : os.path.join(
        dir_var, 'data', 'messages_{0}.mpf.gz'.format(id_task)),
      'rates_csv'     : os.path.join(
        dir_var, 'data', 'rates_{0}.csv.gz'.format(id_task)),
      'channels_csv'  : os.path.join(
        dir_var, 'data', 'channels_{0}.csv.gz'.format(id_task)),
      'latency_csv'   : os.path.join(
        dir_var, 'data', 'latency_{0}.csv.gz'.format(id_task)),
      'aggregate_csv' : os.path.join(
        dir_var, 'data', 'aggregate_{0}.csv.gz'.format(id_task)),
      'usage_log'     : os.path.join(
        dir_var, 'logs', 'usage_{0}.log'.format(id_task)),
      'simout_log'    : os.path.join(
        dir_var, 'logs', 'simout_{0}.log'.format(id_task)),
      'qplot_png'     : os.path.join(
        dir_var, 'plots', 'qplot_{0}.png'.format(id_task)),
      'lplot_png'     : os.path.join(
        dir_var, 'plots', 'lplot_{0}.png'.format(id_task)),
      'cplot_png'     : os.path.join(
        dir_var, 'plots', 'cplot_{0}.png'.format(id_task)),
      'html'          : os.path.join(
        dir_var, 'web_viewer', 'plots.html'),
      'javascript'    : os.path.join(
        dir_var, 'web_viewer', 'dynamic_plot.js'),
      'css'           : os.path.join(
        dir_var, 'web_viewer', 'style.css'),
      'javascript_in' : 'dynamic_plot.js',
      'css_in'        : 'style.css'
    }

  def create_tasks(self, tm_var):
    """
    This creates all the tasks
    """
    # task created only once
    assert not self._created, "Task already created! Fail!"
    self._created = True

    # add load to _variables
    self._variables.append(self._load_variable)

    # check for unique names
    x_values = []
    y_values = []
    for n_var in self._variables:
      x_values.append(n_var['name'])
      y_values.append(n_var['short_name'])
    assert len(x_values) == len(set(x_values)), "Not unique names!"
    assert len(y_values) == len(set(y_values)), "Not unique short names!"

    # generate tasks
    if self._sim:
      print("Creating simulation tasks")
      self._create_sim_tasks(tm_var)
    if self._parse:
      print("Creating parsing tasks")
      self._create_parse_tasks(tm_var)
    if self._qplot:
      print("Creating qplot tasks")
      self._create_qplot_tasks(tm_var)
    if self._lplot:
      print("Creating lplot tasks")
      self._create_lplot_tasks(tm_var)
    if self._cplot:
      print("Creating cplot tasks")
      self._create_cplot_tasks(tm_var)
    if self._web_viewer:
      print("Creating web_viewer")
      self._create_web_viewer_task()

  def _create_sim_tasks(self, tm_var):
    # create config
    for sim_config in self._dim_iter():
      # make id & name
      id_task = self._make_id(sim_config)
      files = self._get_files(id_task)
      sim_name = 'sim_{0}'.format(id_task)
      # sim command
      sim_cmd = ('/usr/bin/time -v -o {0} {1} {2} '
                 'workload.message_log.file=string={3} '
                 'workload.applications[0].rate_log.file=string={4} '
                 'network.channel_log.file=string={5}'
                ).format(
                  files['usage_log'],
                  self._supersim_path,
                  self._settings_path,
                  files['messages_mpf'],
                  files['rates_csv'],
                  files['channels_csv'])
      #loop through each variable commands to add
      for var in sim_config:
        tmp_cmd = var['command'](var['value'], sim_config)
        cmd = self._cmd_clean(tmp_cmd)
        sim_cmd += cmd
      # sim task
      sim_task = taskrun.ProcessTask(tm_var, sim_name, sim_cmd)
      sim_task.stdout_file = files['simout_log']
      sim_task.stderr_file = files['simout_log']
      if self._get_resources is not None:
        sim_task.resources = self._get_resources('sim', sim_config)
      sim_task.priority = 0
      sim_task.add_condition(taskrun.FileModificationCondition(
        [], [files['messages_mpf'], files['rates_csv'], files['channels_csv']]))
      self._sim_tasks[id_task] = sim_task

  def _create_parse_tasks(self, tm_var):
    # loop through all variables
    for parse_config in self._dim_iter():
      # make id and name
      id_task = self._make_id(parse_config)
      files = self._get_files(id_task)
      parse_name = 'parse_{0}'.format(id_task)
      # parse cmd
      parse_cmd = '{0} -{1} {2} -a {3} {4}'.format(
        self._sslatency_path,
        self._latency_mode[:1].lower(),
        files['latency_csv'],
        files['aggregate_csv'],
        files['messages_mpf'])

      if self._parse_scalar is not None:
        parse_cmd += ' -s {0}'.format(self._parse_scalar)
      # parse task
      parse_task = taskrun.ProcessTask(tm_var, parse_name, parse_cmd)
      if self._get_resources is not None:
        parse_task.resources = self._get_resources('parse', parse_config)
      parse_task.priority = 1
      parse_task.add_dependency(self._sim_tasks[id_task])
      parse_task.add_condition(taskrun.FileModificationCondition(
        [files['messages_mpf']],
        [files['latency_csv'], files['aggregate_csv']]))
      self._parse_tasks[id_task] = parse_task

  def _create_qplot_tasks(self, tm_var):
    # loop through all variables
    for qplot_config in self._dim_iter():
      id_task = self._make_id(qplot_config)
      files = self._get_files(id_task)
      qplot_name = 'qplot_{0}'.format(id_task)
      qplot_title = self._make_title(qplot_config, 'qplot')
      qplot_cmd = 'sslqp {0} {1} --title {2} '.format(
        files['latency_csv'],
        files['qplot_png'],
        qplot_title)
      if self._plot_units is not None:
        qplot_cmd += (' --units {0} '.format(self._plot_units))
      qplot_task = taskrun.ProcessTask(tm_var, qplot_name, qplot_cmd)
      if self._get_resources is not None:
        qplot_task.resources = self._get_resources('qplot', qplot_config)
      qplot_task.priority = 1
      qplot_task.add_dependency(self._parse_tasks[id_task])
      qplot_task.add_condition(taskrun.FileModificationCondition(
        [files['latency_csv']],
        [files['qplot_png']]))

  def _create_lplot_tasks(self, tm_var):
    # config with no load
    for lplot_config in self._dim_iter(dont=self._load_name):
      id_task1 = self._make_id(lplot_config)
      lplot_name = 'lplot_{0}'.format(id_task1)
      lplot_title = self._make_title(lplot_config, 'lplot')
      files1 = self._get_files(id_task1)
      # lplot cmd
      lplot_cmd = ('ssllp --row {0} {1} {2} {3} {4} --title {5}'
                   .format(self._latency_mode.title(), files1['lplot_png'],
                           self._start, self._stop + 1, self._step, lplot_title))
      # check plot settings
      if self._plot_units is not None:
        lplot_cmd += (' --units {0}'.format(self._plot_units))
      if self._ymin is not None:
        lplot_cmd += (' --ymin {0}'.format(self._ymin))
      if self._ymax is not None:
        lplot_cmd += (' --ymax {0}'.format(self._ymax))

      # add to lplot_cmd the load files- sweep load
      for loads in  self._dim_iter(do_vars=self._load_name):
        id_task2 = self._make_id(lplot_config, extra=self._make_id(loads))
        files2 = self._get_files(id_task2)
        lplot_cmd += ' {0}'.format(files2['aggregate_csv'])
      # create task
      lplot_task = taskrun.ProcessTask(tm_var, lplot_name, lplot_cmd)
      if self._get_resources is not None:
        lplot_task.resources = self._get_resources('lplot', lplot_config)
      lplot_task.priority = 1
      # add dependencies
      for loads in  self._dim_iter(do_vars=self._load_name):
        id_task3 = self._make_id(lplot_config, extra=self._make_id(loads))
        lplot_task.add_dependency(self._parse_tasks[id_task3])

      lplot_fmc = taskrun.FileModificationCondition([], [files1['lplot_png']])

      # add input files to task
      for loads in self._dim_iter(do_vars=self._load_name):
        id_task4 = self._make_id(lplot_config, extra=self._make_id(loads))
        files3 = self._get_files(id_task4)
        lplot_fmc.add_input(files3['aggregate_csv'])
      lplot_task.add_condition(lplot_fmc)

  def _create_cplot_tasks(self, tm_var):
    # loop over all vars that should compared and have more than 1 value
    for cvar in self._variables:
      if (cvar['name'] is not self._load_name and cvar['compare']
          and len(cvar['values']) > 1):
        # count number of compare variables
        self._comp_var_count += 1
        # iterate all configurations for this variable (no l, no cvar)
        for cplot_config in self._dim_iter(dont=[self._load_name,
                                                 cvar['name']]):
          # iterate all latency distributions (9)
          for field in ssplot.LoadLatencyStats.FIELDS:
            # make id, plot title, png file
            id_task = self._make_id(cplot_config, extra=field)
            cplot_title = self._make_title(cplot_config, 'cplot', cvar=cvar,
                                           lat_dist=field)
            cplot_name = 'cplot_{0}_{1}'.format(cvar['short_name'], id_task)

            files = self._get_files(('{0}_{1}'.format(cvar['short_name'],
                                                      id_task)))

            # cmd
            cplot_cmd = ('sslcp --row {0} --title {1} --field {2} {3} {4} {5} '
                         '{6} '
                         .format(self._latency_mode.title(), cplot_title,
                                 field, files['cplot_png'],
                                 self._start, self._stop + 1, self._step))
            # add plot settings if they exist
            if self._plot_units is not None:
              cplot_cmd += (' --units {0}'.format(self._plot_units))
            if self._ymin is not None:
              cplot_cmd += (' --ymin {0}'.format(self._ymin))
            if self._ymax is not None:
              cplot_cmd += (' --ymax {0}'.format(self._ymax))

            # loop through comp variable and loads to add agg files to cmd
            for var_load_config in self._dim_iter(do_vars=[cvar['name'],
                                                           self._load_name]):
              # create ordered config with cvar and load
              sim_config = self._create_config(cplot_config, var_load_config)
              id_task2 = self._make_id(sim_config)
              files2 = self._get_files(id_task2)
              cplot_cmd += ' {0}'.format(files2['aggregate_csv'])
            # loop through comp variable to create legend
            for var_config in self._dim_iter(do_vars=cvar['name']):
              for var in var_config:
                cplot_cmd += ' --label "{0}"'.format(var['value'])
            # create task
            cplot_task = taskrun.ProcessTask(tm_var, cplot_name, cplot_cmd)
            if self._get_resources is not None:
              cplot_task.resources = self._get_resources('cplot', cplot_config)
            cplot_task.priority = 1
            # add dependencies (loop through load and cvar)
            for var_load_config in self._dim_iter(do_vars=[cvar['name'],
                                                           self._load_name]):
              # create ordered config with cvar and load
              sim_config = self._create_config(cplot_config, var_load_config)
              id_task3 = self._make_id(sim_config)
              cplot_task.add_dependency(self._parse_tasks[id_task3])
            cplot_fmc = taskrun.FileModificationCondition(
              [], [files['cplot_png']])
            for var_load_config in self._dim_iter(do_vars=[cvar['name'],
                                                           self._load_name]):
              # create ordered config with cvar and load
              sim_config = self._create_config(cplot_config, var_load_config)
              id_task4 = self._make_id(sim_config)
              files3 = self._get_files(id_task4)
              cplot_fmc.add_input(files3['aggregate_csv'])
            cplot_task.add_condition(cplot_fmc)

  def _create_web_viewer_task(self):
    files = self._get_files('')

    # css
    css = get_css()
    with open(files['css'], 'w') as fd_css:
      print(css, file=fd_css)

    # html
    html_top = get_html_top(self, files)
    html_bottom = get_html_bottom()
    html_dyn = get_html_dyn(self, ssplot.LoadLatencyStats.FIELDS)

    html_all = html_top + html_dyn + html_bottom
    with open(files['html'], 'w') as fd_html:
      print(html_all, file=fd_html)

    # javascript
    show_div = get_show_div(self)
    cplot_divs = get_cplot_divs(self)
    create_name = get_create_name()
    compose_name = get_compose_name(self)

    js_all = show_div + cplot_divs + create_name + compose_name
    with open(files['javascript'], 'w') as fd_js:
      print(js_all, file=fd_js)
