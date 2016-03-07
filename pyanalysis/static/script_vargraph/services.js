(function () {
    'use strict';

    var module = angular.module('ScriptVarGraph.services', [
        'ng.django.urls',
        'ScriptVarGraph.bootstrap',
        'ngSanitize'
    ]);

    module.factory('ScriptVarGraph.services.Dataset', [
        '$http', 'djangoUrl',
        'ScriptVarGraph.bootstrap.dataset',
        function datasetFactory($http, djangoUrl, datasetId) {
            var apiUrl = djangoUrl.reverse('dataset');

            var Dataset = function () {
                this.id = datasetId
            };

            var request = {
                params: {
                    id: datasetId
                }
            };
            $http.get(apiUrl, request)
                .success(function (data) {
                    angular.extend(Dataset.prototype, data);
                });

            return new Dataset();

        }
    ]);

    //A service for loading script contents.
    module.factory('ScriptVarGraph.services.Script', [
        '$http', 'djangoUrl',
        function scriptFactory($http, djangoUrl) {



            var Script = function () {
                var self = this;
                self.data = undefined;
                self.script_data = undefined;
            };

            angular.extend(Script.prototype, {
                load: function (script_id) {
                    var self = this;
                    var apiUrl = djangoUrl.reverse('script');

                    var request = {
                        params: {
                            id: script_id
                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.data = data;
                        });

                },
                load_vargraph: function (script_id) {
                    var self = this;
                    var apiUrl = djangoUrl.reverse('vargraph');

                    var request = {
                        params: {
                            id: script_id
                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.script_data = data;
                        });

                }
            });

            return new Script();
        }
    ]);


})();
