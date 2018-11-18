var higlass_jupyter = require('./index');

var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'jupyter.extensions.higlass-jupyter',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'higlass-jupyter',
          version: higlass_jupyter.version,
          exports: higlass_jupyter
      });
  },
  autoStart: true
};