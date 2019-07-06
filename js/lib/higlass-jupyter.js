var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var hglib_css = require('higlass/dist/hglib.css');
var hglib = require('higlass/dist/hglib.js');
var packageJson = require('../package.json');

var HiGlassDisplayModel = widgets.DOMWidgetModel.extend({
  defaults: _.extend(
    _.result(this, 'widgets.DOMWidgetModel.prototype.defaults'),
    {
      _model_name : 'HiGlassDisplayModel',
      _view_name : 'HiGlassDisplayView',
      _model_module : 'higlass-jupyter',
      _view_module : 'higlass-jupyter',
      _model_module_version : packageJson.version,
      _view_module_version : packageJson.version
    }
  )
});

// Custom View. Renders the widget model.
var HiGlassDisplayView = widgets.DOMWidgetView.extend({
  render: function() {
    var viewConfig = this.model.get('viewconf');
    var height = this.model.get('height');
    var hgOptions = this.model.get('hg_options');

    var borderColor = hgOptions.isDarkTheme ? '#333333' : '#dddddd'

    this.hgcontainer = document.createElement('div');
    this.hgdisplay = document.createElement('div');
    this.hgdisplay.style.border = '1px solid #dddddd';
    this.hgdisplay.style.borderRadius = '2px';

    this.hgcontainer.appendChild(this.hgdisplay);
    this.el.appendChild(this.hgcontainer);

    if (height) {
      this.hgdisplay.style.height = height + 'px';


      if (typeof hgOptions.bounded === 'undefined') {
        // user hasn't specified a bounded but provided a height so we set
        // bounded to `true`
        hgOptions['bounded'] = true;
      }
    }

    hglib.viewer(
      this.hgdisplay,
      viewConfig,
      hgOptions,
      function (api) {
        window.hgApi = api;
      }
    );
  }
});

module.exports = {
  HiGlassDisplayModel: HiGlassDisplayModel,
  HiGlassDisplayView: HiGlassDisplayView
};
