var jupyter_higlass = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'jupyter.extensions.jupyter-higlass',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'jupyter-higlass',
          version: jupyter_higlass.version,
          exports: jupyter_higlass
      });
  },
  autoStart: true
};