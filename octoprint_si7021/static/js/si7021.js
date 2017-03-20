$(function() {
  function Si7021ViewModel(parameters) {
    var self = this;

    self.si7021Model = parameters[0];
    self.global_settings = parameters[1];
    self.si7021 = ko.observable();
    self.isRaspi = ko.observable(false);

    self.onBeforeBinding = function () {
      self.settings = self.global_settings.settings.plugins.si7021;
    };

    self.onDataUpdaterPluginMessage = function(plugin, data) {
      if (plugin != 'si7021') {
        return;
      }

      if (!data.hasOwnProperty('israspi')) {
        self.isRaspi(false);
      } else {
        self.isRaspi(true);
      }

      self.si7021(
        _.sprintf(
          "Room: %.1f&percnt; | %.1f&deg;C | %.1f&deg;F",
          data.rh,
          data.tc,
          data.tf
        )
      );
    };
  }

  ADDITIONAL_VIEWMODELS.push([
    Si7021ViewModel,
    ['temperatureViewModel', 'settingsViewModel'],
    ['#navbar_plugin_si7021', '#settings_plugin_si7021']
  ]);
});
