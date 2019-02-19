var jupyter_higlass = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'jupyter.extensions.higlass-python',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'higlass-python',
          version: jupyter_higlass.version,
          exports: jupyter_higlass
      });
  },
  autoStart: true
};
