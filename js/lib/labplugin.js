var jupyter_higlass = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'jupyter.extensions.higlass-jupyter',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'higlass-jupyter',
          version: jupyter_higlass.version,
          exports: jupyter_higlass
      });
  },
  autoStart: true
};
