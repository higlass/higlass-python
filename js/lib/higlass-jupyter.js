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
  render: function render() {
    var viewConfig = this.model.get('viewconf');
    var height = this.model.get('height');
    var hgOptions = this.model.get('hg_options');

    this.hgcontainer = document.createElement('div');
    this.hgdisplay = document.createElement('div');
    this.hgdisplay.style.border = hgOptions.theme === 'dark'
      ? '#333333' : '#dddddd';
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

    var sendMsgToPython = this.send.bind(this);

    function forwardEvent(eventName) {
      return function sendMessage() {
        // This is the same as using ES6's ...args
        var args = Array.prototype.slice.call(arguments);
        if (eventName === 'selection') console.log('selected', args);
        sendMsgToPython({
          type: eventName,
          data: args
        })
      };
    }

    this.hg = hglib.viewer(this.hgdisplay, viewConfig, hgOptions);

    window.hgApi = this.hg;

    this.hg.on('location', forwardEvent('location'));
    this.hg.on('cursorLocation', forwardEvent('cursor_location'));
    this.hg.on('rangeSelection', forwardEvent('selection'));

    // Listen to messages from the Python world
    this.model.on("change:select_mode", this.handleChange, this)
  },

  handleChange: function () {
    var self = this;
    var changes = this.model.changedAttributes();
    Object.keys(changes).forEach(function (key) {
      var value = changes[key];
      switch (key) {
        case 'select_mode':
          self.hg.activateTool(value && 'select');
          break;

        default:
          console.warn('Unknown attribute', key);
          break;
      }
    });
  }
});

module.exports = {
  HiGlassDisplayModel: HiGlassDisplayModel,
  HiGlassDisplayView: HiGlassDisplayView
};
