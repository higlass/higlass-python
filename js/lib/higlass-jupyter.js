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
    this.height = this.model.get('height');
    this.viewConfig = this.model.get('viewconf');
    this.authToken = this.model.get('auth_token');
    this.bounded = this.model.get('bounded');
    this.defaultTrackOptions = this.model.get('default_track_options');
    this.darkMode = this.model.get('dark_mode');
    this.renderer = this.model.get('renderer');
    this.selectMode = this.model.get('select_mode');
    this.selectionOnAlt = this.model.get('selection_on_alt');
    this.options = this.model.get('options');

    // Create a random 6-letter string
    // From https://gist.github.com/6174/6062387
    var randomStr = (
      Math.random().toString(36).substring(2, 5) +
      Math.random().toString(36).substring(2, 5)
    );
    this.model.set('dom_element_id', randomStr);

    this.hgContainer = document.createElement('div');
    this.hgContainer.setAttribute('id', randomStr);
    this.hgDisplay = document.createElement('div');
    this.hgDisplay.style.border = this.options.theme === 'dark'
      ? '#333333' : '#dddddd';
    this.hgDisplay.style.borderRadius = '2px';

    this.hgContainer.appendChild(this.hgDisplay);
    this.el.appendChild(this.hgContainer);

    this.hg = hglib.viewer(this.hgDisplay, this.viewConfig, this.getOptions());

    this.hgContainer.api = this.hg;

    // Listen to events from the JavaScript world
    this.hg.on('cursorLocation', this.setCursorLocation.bind(this));
    this.hg.on('rangeSelection', this.setSelection.bind(this));
    this.hg.on('viewConfig', this.setViewConfig.bind(this));

    this.locationListeners = [];
    this.setupLocationListeners();

    // Listen to messages from the Python world
    this.model.on("change:height", this.handleChange, this);
    this.model.on("change:select_mode", this.handleChange, this);
    this.model.on("change:viewconf", this.handleChange, this);
    this.model.on("change:auth_token", this.handleChange, this);
    this.model.on("change:bounded", this.handleChange, this);
    this.model.on("change:default_track_options", this.handleChange, this);
    this.model.on("change:dark_mode", this.handleChange, this);
    this.model.on("change:renderer", this.handleChange, this);
    this.model.on("change:select_mode", this.handleChange, this);
    this.model.on("change:selection_on_alt", this.handleChange, this);
    this.model.on('msg:custom', this.customEventHandler, this);

  },

  customEventHandler: async function(msg) {
    const msgJson = JSON.parse(msg);

    console.log('msgJson:', msgJson);

    this.hg.exportAsPngBlobPromise().then(blob => {
     let reader = new FileReader();
     reader.readAsDataURL(blob);
     reader.onloadend = () => {
         let base64data = reader.result;
         this.model.send({
           imgData: base64data,
           request: msgJson.request,
           params: msgJson.params,
         })
     }
    });

    if (msgJson.request === 'save_as_png') {
      this.model.send({
        'params': msgJson.params,

      });
    }
  },

  getOptions: function() {
    return Object.assign({}, this.options, {
      authToken: this.authToken,
      // user hasn't specified `bounded` but provided a height so we set
      // bounded to `true`
      bounded: this.height && this.bounded === null
        ? true : this.bounded,
      defaultTrackOptions: this.defaultTrackOptions,
      rangeSelectionOnAlt: this.selectionOnAlt,
      renderer: this.renderer,
      theme: this.darkMode ? 'dark' : 'light'
    });
  },

  setupLocationListeners: function() {
    function removeLocationListener(locationListener) {
      this.hg.off('location', locationListener);
    }
    this.locationListeners.forEach(removeLocationListener.bind(this));
    this.locationListeners = [];
    function addLocationListener(view, index) {
      this.locationListeners.push(this.hg.on(
        'location',
        this.setLocation(index, this.viewConfig.views.length === 1),
        view.uid
      ));
    }
    this.viewConfig.views.forEach(addLocationListener.bind(this))

  },

  setCursorLocation: function (cursorLocation) {
    this.model.set('cursor_location', [
      cursorLocation.dataX,
      cursorLocation.dataY
    ]);
    this.model.save_changes();
  },

  setLocation: function (index, onlyOneView) {
    function setLocation(location) {
      var loc = [
        location.xDomain[0],
        location.xDomain[1],
        location.yDomain[0],
        location.yDomain[1]
      ];
      if (!onlyOneView) {
        var currentLocations = this.model.get('location').slice();
        currentLocations[index] = loc;
        loc = currentLocations;
      }
      this.model.set('location', loc);
      this.model.save_changes();
    }
    return setLocation.bind(this);
   },

  setSelection: function (selection) {
    this.model.set('selection', [
      selection.dataRange[0] && selection.dataRange[0][0],
      selection.dataRange[0] && selection.dataRange[0][1],
      selection.dataRange[1] && selection.dataRange[1][0],
      selection.dataRange[1] && selection.dataRange[1][1]
    ]);
    this.model.save_changes();
  },

  setViewConfig: function (viewConfigString) {
    this.viewConfig = JSON.parse(viewConfigString);
    this.model.set('viewconf', this.viewConfig);
    // We need this to avoid cyclic updates because `this.handleChange` will be
    // called next. The downside of 2-way data binding.
    this.viewconfChanged = true;
    this.model.save_changes();
  },

  handleChange: function () {
    var self = this;
    var changes = this.model.changedAttributes();
    Object.keys(changes).forEach(function (key) {
      var value = changes[key];
      switch (key) {
        case 'height':
          self.height = value;
          self.hgDisplay.style.height = self.height + 'px';
          break;

        case 'auth_token':
          self.authToken = value;
          self.hg = hglib.viewer(self.hgDisplay, self.viewConfig, self.getOptions());
          break;

        case 'bounded':
          self.bounded = value;
          self.hg = hglib.viewer(self.hgDisplay, self.viewConfig, self.getOptions());
          break;

        case 'default_track_options':
          self.defaultTrackOptions = value;
          self.hg = hglib.viewer(self.hgDisplay, self.viewConfig, self.getOptions());
          break;

        case 'dark_mode':
          self.darkMode = value;
          self.hg = hglib.viewer(self.hgDisplay, self.viewConfig, self.getOptions());
          break;

        case 'renderer':
          self.renderer = value;
          self.hg = hglib.viewer(self.hgDisplay, self.viewConfig, self.getOptions());
          break;

        case 'selection_on_alt':
          self.selectionOnAlt = value;
          self.hg = hglib.viewer(self.hgDisplay, self.viewConfig, self.getOptions());
          break;

        case 'options':
          self.options = value;
          self.hg = hglib.viewer(self.hgDisplay, self.viewConfig, self.getOptions());
          break;

        case 'select_mode':
          self.hg.activateTool(value && 'select');
          break;

        case 'viewconf':
          if (!self.viewconfChanged) {
            self.viewConfig = typeof value === 'string' ? JSON.parse(value) : value;
            self.hg.setViewConfig(self.viewConfig);
          }
          break;

        default:
          console.warn('Unknown attribute', key);
          break;
      }
    });
    this.viewconfChanged = false;
  }
});

module.exports = {
  HiGlassDisplayModel: HiGlassDisplayModel,
  HiGlassDisplayView: HiGlassDisplayView
};
