(function () {
    'use strict';

    var module = angular.module('ScriptBrowser.services', [
        'ng.django.urls',
        'ScriptBrowser.bootstrap',
        'ngSanitize'
    ]);

    module.factory('ScriptBrowser.services.Dataset', [
        '$http', 'djangoUrl',
        'ScriptBrowser.bootstrap.dataset',
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


    //A service for loading similarity graph.
    module.factory('ScriptBrowser.services.SimilarityGraph', [
        '$http', 'djangoUrl',
        function similarityGraphFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('similarity-graph');

            var SimilarityGraph = function () {
                var self = this;
                self.data = undefined;
            };

            angular.extend(SimilarityGraph.prototype, {
                load: function (dataset) {
                    var self = this;

                    var request = {
                        params: {
                            id: dataset
                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.data = data;
                        });

                }
            });

            return new SimilarityGraph();
        }
    ]);


    //A service for loading script contents.
    module.factory('ScriptBrowser.services.Script', [
        '$http', 'djangoUrl',
        function scriptFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('script');

            var Script = function () {
                var self = this;
                self.data = undefined;
            };

            angular.extend(Script.prototype, {
                load: function (script_id) {
                    var self = this;

                    var request = {
                        params: {
                            id: script_id
                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.data = data;
                        });

                }
            });

            return new Script();
        }
    ]);

})();
